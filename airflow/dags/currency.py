import os
import json
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from datetime import datetime,timedelta

def on_failure_callback(**context):
    print(f"Task {context['task_instance_key_str']} failed.")

def uploadtomongo(ti, **context):
    try:
        print("Trying to connect")
        hook = MongoHook(mongo_conn_id='mongo_default')
        client = hook.get_conn()
        db = client.MyDB
        currency_collection=db.currency_collection
        print(f"Connected to MongoDB - {client.server_info()}")
        d=json.loads(context["result"])
        currency_collection.insert_one(d)
    except Exception as e:
        print(f"Error connecting to MongoDB -- {e}")

with DAG(
    dag_id="load_currency_data",
    schedule_interval=None,
    start_date=datetime(2022,10,28),
    catchup=False,
    tags= ["currency"],
    default_args={
        "owner": "Rob",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        'on_failure_callback': on_failure_callback
    }
) as dag:

    t1 = SimpleHttpOperator(
        task_id='get_currency',
        method='GET',
        endpoint='2022-01-01..2022-06-30',
        headers={"Content-Type": "application/json"},
        do_xcom_push=True,
        dag=dag)

    t2 = PythonOperator(
        task_id='upload-mongodb',
        python_callable=uploadtomongo,
        op_kwargs={"result": t1.output},
        dag=dag
        )

    t1 >> t2