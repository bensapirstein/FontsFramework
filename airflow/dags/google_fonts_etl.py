from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.models.param import Param
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
            'num_fonts' : 1,
            'categories' : ["sans-serif"],
            'subsets' : ['hebrew', 'arabic'],
            'font_folder' : "google_fonts",
            'data_file' : 'google_fonts.csv',
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

    # Define the transform task
    @task
    def transform(**kwargs):
        params = kwargs['params']
        # Convert the fonts to UFO format
        converted_df = font_downloader.convert_df_to_ufo(params['data_file'], params['font_folder'])
        

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
    extract() >> transform() >> load()
