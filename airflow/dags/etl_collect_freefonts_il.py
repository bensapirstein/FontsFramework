from airflow import DAG
from airflow.decorators import task
from datetime import datetime
from include.web_scraping import download_fonts_from_url
from include.data_collection import convert_folder_to_ufo, upload_ufos

with DAG("etl_collect_freefonts_il", start_date=datetime(2023, 1, 1), schedule_interval="@daily",
    catchup=False) as dag:

    @task
    def extract(url, out_path):
        download_fonts_from_url(url, out_path)

    @task
    def transform(fonts_path):
        convert_folder_to_ufo(fonts_path)

    @task 
    def load(fonts_path):
        upload_ufos(fonts_path)

    extract("http://freefonts.co.il/", "freefonts_il") >> transform("freefonts_il") >> load("freefonts_il")