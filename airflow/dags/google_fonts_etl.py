from airflow import DAG
from airflow.decorators import task, task_group
from airflow.models import Variable
from airflow.operators.python import PythonOperator, get_current_context
from airflow.utils.task_group import TaskGroup
from airflow.providers.mongo.hooks.mongo import MongoHook
from datetime import datetime
import data.data_collection as font_downloader
# Initialize the DAG

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
            'data_file' : 'google_fonts.csv',
            'num_parallel_tasks' : 2
        }
    ) as dag:
    # Define the extract task
    @task
    def extract(**kwargs):
        params = kwargs['params']
        # Fetch the fonts information from the Google Fonts API
        fonts_df = font_downloader.get_fonts_info(Variable.get('GOOGLE_FONTS_API_KEY'))
        filtered_df = font_downloader.filter_fonts(fonts_df, num_fonts=params['num_fonts'], 
                                                    categories=params['categories'],
                                                    subsets=params['subsets'])
        # Download the fonts
        downloaded_df = font_downloader.download_fonts(filtered_df, params['font_folder'])
        downloaded_df.to_csv(params['data_file'])
        # push the number of rows in the data file to xcom
        kwargs['ti'].xcom_push(key='num_rows', value=len(downloaded_df))

    # Define the transform task
    @task
    def transform_task(task_index, **kwargs):
        params = kwargs['params']
        # Get the number of rows from xcom
        num_rows = kwargs['ti'].xcom_pull(key='num_rows', task_ids='extract')
        # Get the number of parallel tasks from params
        num_parallel_tasks = params['num_parallel_tasks']
        # Get the current task instance
        task_instance = get_current_context()['task_instance']
        # Get the number of rows per task
        rows_per_task = num_rows // num_parallel_tasks
        # Get the start and end rows
        start_row = task_index * rows_per_task
        if task_index == num_parallel_tasks - 1:
            end_row = num_rows
        else:
            end_row = (task_index + 1) * rows_per_task
        # Log the start and end rows
        task_instance.log.info(f"Start row: {start_row}")
        task_instance.log.info(f"End row: {end_row}")
        # Convert the fonts to UFO format
        font_downloader.convert_df_to_ufo(params['data_file'], params['font_folder'], list(range(start_row, end_row)))

    # Create transform task group
    @task_group(group_id='transform_group')
    def transform_group(num_parallel_tasks):
        # Define the parallel tasks
        return [transform_task(i) for i in range(num_parallel_tasks)]

    # Define the load task
    @task
    def load():
        # Connect to the MongoDB sharded cluster
        hook = MongoHook(mongo_conn_id='mongo_default')
        client = hook.get_conn()
        db = client.FontsFramework
        ufo_collection = db.ufo_collection

        # Upload the UFO files to MongoDB
        failed_cases = font_downloader.upload_ufos(ufo_collection)
        return failed_cases

    # Define the DAG dependencies
    extract() >> transform_group(dag.params['num_parallel_tasks']) >> load()
