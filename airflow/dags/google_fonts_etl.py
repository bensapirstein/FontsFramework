from airflow import DAG
from airflow.decorators import task, task_group
from airflow.models import Variable
from airflow.operators.python import PythonOperator, get_current_context
from airflow.utils.task_group import TaskGroup
from airflow.providers.mongo.hooks.mongo import MongoHook
from datetime import datetime
import data.data_collection as font_downloader
import numpy as np
import pandas as pd
# Initialize the DAG

def get_start_end_rows(num_parallel_tasks, task_index, num_rows):
    """
    Returns the start and end row indices for each task

    Parameters
    ----------
    num_parallel_tasks : int
        The number of parallel tasks
    task_index : int
        The index of the task
    num_rows : int
        The number of rows in the data file

    Returns
    -------
    list
        The start and end row indices for each task
    """
    rows_per_task = num_rows // num_parallel_tasks
    start_row = task_index * rows_per_task
    end_row = start_row + rows_per_task
    if task_index == num_parallel_tasks - 1:
        end_row = num_rows

    return list(range(start_row, end_row))

with DAG(
        "google_fonts_etl", 
        start_date=datetime(2023, 1, 1),
        schedule_interval="@daily", 
        catchup=False,
        params={
            'num_fonts' : 4,
            'categories' : ["sans-serif"],
            'subsets' : ['hebrew', 'arabic'],
            'font_folder' : "google_fonts",
            'info_file' : 'google_fonts.csv',
            'ufo_file' : 'ufo_data.csv',
            'num_parallel_tasks' : 2
        }
    ) as dag:
    

    @task
    def get_fonts_info(**context):
        params = context['params']
        fonts_df = font_downloader.get_fonts_info(Variable.get('GOOGLE_FONTS_API_KEY'))
        fonts_df.to_csv(params['info_file'])

    @task
    def filter_fonts(**context):
        params = context['params']
        fonts_df = pd.read_csv(params['info_file'])
        filtered_df = font_downloader.filter_fonts(fonts_df, num_fonts=params['num_fonts'], 
                                                    categories=params['categories'],
                                                    subsets=params['subsets'])
        filtered_df.to_csv(params['info_file'])

    @task
    def download_fonts_task(num_tasks, task_index, **context):
        params = context['params']
        filtered_df = pd.read_csv(params['info_file'])
        rows_range = get_start_end_rows(num_tasks, task_index, len(filtered_df))
        # Log the task index and the rows range
        print(f"Task index: {task_index}, rows range: {rows_range}")
        # Download the fonts
        downloaded_df = font_downloader.download_fonts(filtered_df.iloc[rows_range], params['font_folder'])
        # save task_index and downloaded_df to csv
        downloaded_df.to_csv(f"downloaded_df_{task_index}.csv")

    # Unite all downloaded_df to one csv file
    @task
    def unite_downloaded_df(num_task, **context):
        params = context['params']
        downloaded_df = pd.DataFrame()
        num_tasks = params['num_parallel_tasks']
        for i in range(num_tasks):
            downloaded_df = pd.concat([downloaded_df, pd.read_csv(f"downloaded_df_{i}.csv")])
        print(f"Total downloaded fonts: {len(downloaded_df)}")
        downloaded_df.to_csv(params['info_file'])

    @task_group
    def download_fonts(num_tasks):
        return [download_fonts_task(num_tasks, i) for i in range(num_tasks)]

    @task_group
    def extract(num_tasks):
        get_fonts_info() >> filter_fonts() >> download_fonts(num_tasks) >> unite_downloaded_df(num_tasks)

    # Define the transform task
    @task
    def transform_task(num_tasks, task_index, **kwargs):
        params = kwargs['params']
        downloaded_df = pd.read_csv(params['info_file'])

        rows_range = get_start_end_rows(num_tasks, task_index, len(downloaded_df))
        
        # Log the task index and the rows range
        print(f"Task index: {task_index}, rows range: {rows_range}")
        print(f"Task {task_index} downloaded fonts: {len(downloaded_df)}")

        # Convert the fonts to UFO format
        ufo_df = font_downloader.convert_df_to_ufo(downloaded_df.iloc[rows_range], params['font_folder'])
        # save task_index and ufo_df to csv
        ufo_df.to_csv(f"ufo_df_{task_index}.csv")

    @task
    def unite_ufo_df(num_tasks, **context):
        params = context['params']
        ufo_df = pd.DataFrame()
        for i in range(num_tasks):
            df_i = pd.read_csv(f"ufo_df_{i}.csv")
            print(f"Task {i} UFOs: {len(df_i)}")
            print(df_i.head())
            ufo_df = pd.concat([ufo_df, df_i])
        print("United UFOs, total number of UFOs: ", len(ufo_df))
        ufo_df.to_csv(params['ufo_file'])

    # Create transform task group
    @task_group(group_id='transform')
    def transform(num_tasks):
        [transform_task(num_tasks, i) for i in range(num_tasks)] >> unite_ufo_df(num_tasks)

    # Define the load task
    @task
    def load(**context):
        params = context['params']
        # Connect to the MongoDB sharded cluster
        hook = MongoHook(mongo_conn_id='mongo_default')
        client = hook.get_conn()
        db = client.FontsFramework
        ufo_collection = db.ufo_collection
        
        # Upload the UFO files to MongoDB
        failed_cases = font_downloader.upload_ufos(params['ufo_file'] ,ufo_collection)
        return failed_cases

    # Define the DAG dependencies
    n = dag.params['num_parallel_tasks']
    extract(n * 2) >> transform(n) >> load()
