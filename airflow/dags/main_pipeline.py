from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from datetime import datetime,timedelta

def google_fonts_api_func():
    # code to download google fonts
    pass

def crawl_web_fonts_func():
    # code to crawl web fonts
    pass

def upload_local_folder_func():
    # code to upload local folder
    pass

def upload_to_mongoDB_func():
    try:
        # Connect to the MongoDB sharded cluster
        data_engine = FontStorage()
        # Add the UFO font to the database
        data_engine.add_ufo_font(ufo_path, family, variant)
    except Exception as e:
        print(f"Error connecting to MongoDB -- {e}")


def fetch_glyph_dataset_func():
    # code to fetch glyph dataset
    pass

def on_failure_callback(**context):
    print(f"Task {context['task_instance_key_str']} failed.")

with DAG(
    dag_id="collect_data",
    schedule_interval=None,
    start_date=datetime(2022,10,28),
    catchup=False,
    default_args={
        "owner": "Bob",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        'on_failure_callback': on_failure_callback
    },
    tags= ["fonts"]
    ) as dag:
        
    download_google_fonts = PythonOperator(
        task_id='google_fonts_api',
        python_callable=google_fonts_api_func,
        dag=dag
    )
    
    crawl_web_fonts = PythonOperator(
        task_id='crawl_web_fonts',
        python_callable=crawl_web_fonts_func,
        dag=dag
    )
    
    upload_local_folder = PythonOperator(
        task_id='upload_local_folder',
        python_callable=upload_local_folder_func,
        dag=dag
    )
    
    #Data Ingestion
    convert_to_ufo = BashOperator(
        task_id='convert_to_ufo',
        bash_command='convert_fonts_to_ufo.sh', 
        dag=dag)
    
    #Data storage
    upload_to_mongoDB = PythonOperator(
        task_id='upload_to_mongoDB',
        python_callable=upload_to_mongoDB_func,
        dag=dag
    )

    # set task dependencies
    download_google_fonts >> convert_to_ufo
    crawl_web_fonts >> convert_to_ufo
    upload_local_folder >> convert_to_ufo 
    convert_to_ufo >> upload_to_mongoDB