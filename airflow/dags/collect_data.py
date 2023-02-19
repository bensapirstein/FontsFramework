import os
import json
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from datetime import datetime,timedelta
from airflow.models import Variable

from include.data_collection import get_fonts_info, filter_fonts, download_fonts, convert_df_to_ufo, upload_ufos

def google_fonts_api_func():
    fonts_df = get_fonts_info(Variable.get('GOOGLE_FONTS_API_KEY'))
    
    # code to download google fonts
    fonts_path = "data/raw/fonts/"
    data_file = "download_data.csv"
    filtered_df = filter_fonts(fonts_df, subsets=['hebrew', 'arabic'])
    
    fonts_to_download = download_fonts(filtered_df, os.path.join(fonts_path, "GF"))
    fonts_to_download.to_csv(data_file, index=False)


def crawl_web_fonts_func():
    # code to crawl web fonts
    pass

def upload_local_folder_func():
    # code to upload local folder
    pass

def convert_fonts_to_ufo_func():
    convert_df_to_ufo("download_data.csv", "data/raw/fonts/")

def upload_to_mongoDB_func():
    try:
        # Connect to the MongoDB sharded cluster
        hook = MongoHook(mongo_conn_id='mongo_default')
        client = hook.get_conn()
        db = client.FontsFramework
        ufo_collection = db.ufo_collection
        print(f"Connected to MongoDB - {client.server_info()}")

        upload_ufos(ufo_collection)
        # Add the UFO font to the database
        #data_engine.add_ufo_font(ufo_path, family, variant)
    except Exception as e:
        print(f"Error connecting to MongoDB -- {e}")

def on_failure_callback(**context):
    print(f"Task {context['task_instance_key_str']} failed.")

with DAG(
    dag_id="collect_data",
    schedule_interval=None,
    start_date=datetime(2022,10,28),
    catchup=False,
    default_args={
        "owner": "Ben Fouad Roni",
        "retries": 0,
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
    convert_to_ufo = PythonOperator(
        task_id='convert_to_ufo',
        python_callable=convert_fonts_to_ufo_func, 
        dag=dag)
    
    #Data storage
    upload_to_mongoDB = PythonOperator(
        task_id='upload_to_mongoDB',
        python_callable=upload_to_mongoDB_func,
        dag=dag
    )

    # set task dependencies
    [download_google_fonts, crawl_web_fonts, upload_local_folder] >> convert_to_ufo
    convert_to_ufo >> upload_to_mongoDB