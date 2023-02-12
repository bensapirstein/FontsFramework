from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import BranchPythonOperator
from datetime import datetime

from airflow.decorators import task, task_group

from airflow.providers.mongo.hooks.mongo import MongoHook

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email': [''],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

with DAG(
        "generate_fonts", 
        start_date=datetime(2023, 1, 1),
        schedule_interval="@daily", 
        catchup=False,
        params={
            'num_fonts' : 1,
            'categories' : ["sans-serif"],
            'subsets' : ['hebrew', 'arabic'],
            'font_folder' : "generated_fonts",
            'num_parallel_tasks' : 2
        }
    ) as dag:

    @task
    def get_ufo_from_mongo():
        # get ufo from mongo
        hook = MongoHook(mongo_conn_id='mongo_default')
        client = hook.get_conn()
        db = client.FontsFramework
        ufo_collection = db.ufo_collection

        pass

    @task
    def generate_woff():
        # generate woff
        pass

    @task
    def generate_woff2():
        # generate woff2
        pass

    @task
    def generate_ttf():
        # generate ttf
        pass

    @task
    def generate_otf():
        # generate otf
        pass

    @task_group(group_id="generate_formats")
    def generate_formats():
        # generate fonts in parallel using the above tasks
        return [generate_woff(), generate_woff2(), generate_ttf(), generate_otf()]
        

    @task
    def upload_fonts_to_mongo():
        # upload fonts to mongo
        pass

    # Define the Dag structure
    get_ufo_from_mongo() >> generate_formats() >> upload_fonts_to_mongo()
