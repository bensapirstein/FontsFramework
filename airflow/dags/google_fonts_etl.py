from airflow import DAG
from airflow.decorators import task, task_group
from airflow.models import Variable
from include.mongo_utils import get_ufo_collection
from datetime import datetime
import include.data_collection as data_collection
import pandas as pd
import json
import os
import shutil
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
        max_active_tasks=8, # We will run a task per font so we need to limit the number of active tasks
        params={
            'num_fonts' : 6,
            'categories' : None,
            'subsets' : ['hebrew', 'arabic'],
            'font_folder' : "google_fonts",
            'info_folder' : 'fonts_info',
            'info_file' : 'fonts_info/fonts_info.csv',
            'downloaded_file' : 'fonts_info/downloaded_fonts.csv',
            'filtered_info_file' : 'fonts_info/filtered_fonts_info.csv',
            'ufo_file' : 'fonts_info/ufo_data.csv',
            'num_parallel_tasks' : 2
        }
    ) as dag:
    

    @task
    def get_fonts_info(**context):
        params = context['params']

        if not os.path.exists(params['info_folder']):
            os.mkdir(params['info_folder'])
        
        fonts_df = data_collection.get_fonts_info(Variable.get('GOOGLE_FONTS_API_KEY'))
        print(f"Total fonts: {len(fonts_df)}")
        fonts_df.to_csv(params['info_file'])

    @task
    def filter_fonts(**context):
        params = context['params']
        fonts_df = pd.read_csv(params['info_file'])
        filtered_df = data_collection.filter_fonts(fonts_df, num_fonts=params['num_fonts'], 
                                                    categories=params['categories'],
                                                    subsets=params['subsets'],
                                                    ufo_collection=get_ufo_collection("FontsFramework", "UFOs"))
        print(filtered_df.head())
        filtered_df.to_csv(params['filtered_info_file'])

    @task
    def download_fonts_task(num_tasks, task_index, **context):
        params = context['params']
        filtered_df = pd.read_csv(params['filtered_info_file'])
        rows_range = get_start_end_rows(num_tasks, task_index, len(filtered_df))
        # Log the task index and the rows range
        print(f"Task index: {task_index}, rows range: {rows_range}")
        # Download the fonts
        downloaded_df = data_collection.download_fonts(filtered_df.iloc[rows_range], params['font_folder'])

        print(f"Task {task_index} downloaded fonts: {len(downloaded_df)}")

        # save task_index and downloaded_df to csv
        downloaded_df.to_csv(f"{params['info_folder']}/downloaded_df_{task_index}.csv")

    # Unite all downloaded_df to one csv file
    @task
    def unite_downloaded_df(num_tasks, **context):
        params = context['params']
        downloaded_df = pd.DataFrame()
        for i in range(num_tasks):
            downloaded_df = pd.concat([downloaded_df, pd.read_csv(f"{params['info_folder']}/downloaded_df_{i}.csv")])
        print(f"Total downloaded fonts: {len(downloaded_df)}")
        downloaded_df.to_csv(params['downloaded_file'])

    @task_group
    def download_fonts(num_tasks):
        return [download_fonts_task(num_tasks, i) for i in range(num_tasks)]

    @task_group
    def extract(num_tasks):
        get_fonts_info() >> filter_fonts() >> download_fonts(num_tasks) >> unite_downloaded_df(num_tasks)

    @task
    def transform_task(num_tasks, task_index, **kwargs):
        params = kwargs['params']
        downloaded_df = pd.read_csv(params['downloaded_file'])

        rows_range = get_start_end_rows(num_tasks, task_index, len(downloaded_df))
        
        # Log the task index and the rows range
        print(f"Task index: {task_index}, rows range: {rows_range}")
        print(f"Task {task_index} downloaded fonts: {len(downloaded_df)}")

        # Convert the fonts to UFO format
        ufo_df = data_collection.convert_df_to_ufo(downloaded_df.iloc[rows_range], params['font_folder'])
        # return ufo_df as json
        return ufo_df.to_json()

    @task
    def unite_ufo_df(num_tasks, ufo_dfs, **context):
        ufo_df = pd.DataFrame()
        for i in range(num_tasks):
            df_i = pd.DataFrame.from_dict(json.loads(ufo_dfs[i]))
            print(f"Task {i} UFOs: {len(df_i)}")
            print(df_i.head())
            ufo_df = pd.concat([ufo_df, df_i])
        print("United UFOs, total number of UFOs: ", len(ufo_df))
        params = context['params']
        ufo_df.to_csv(params['ufo_file'])

    # Create transform task group
    @task_group(group_id='transform')
    def transform(num_tasks):
        t_group = [transform_task(num_tasks, i) for i in range(num_tasks)]

        unite_ufo_df(num_tasks, t_group)
        #return { 'ufo_df': t_group}

    # TODO: Change load to be a task group where each task uploads a single UFO, and the task group waits for all tasks to finish
    # there could only be N tasks running at the same time, where N is the number of parallel tasks

    # Define the load task
    @task
    def load(**context):
        params = context['params']
        # Get the UFO collection
        ufo_collection = get_ufo_collection("FontsFramework", "UFOs")
        
        # Upload the UFO files to MongoDB
        failed_cases = data_collection.upload_ufos(params['ufo_file'] ,ufo_collection)

        # Cleanup the info folder
        shutil.rmtree(params['info_folder'])

        return failed_cases

    # Define the DAG dependencies
    n = dag.params['num_parallel_tasks']
    extract(n + 1) >> transform(n) >> load()
