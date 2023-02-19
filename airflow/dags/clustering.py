from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.papermill.operators.papermill import PapermillOperator
from airflow.decorators import task
from include.mongo_utils import get_ufo_collection
import pandas as pd
from airflow.providers.mongo.hooks.mongo import MongoHook
import json

with DAG(
    dag_id='clustering',
    default_args={
        'retries': 0
    },
    schedule='0 0 * * *',
    start_date=datetime(2022, 10, 1),
    template_searchpath='/usr/local/airflow/include/',
    catchup=False
) as dag:

    @task
    def prepare_clustering_data():
        ufo_collection = get_ufo_collection("FontsFramework", "UFOs")
        fonts = ufo_collection.find({"granulated_data": {"$exists": True}}, {"family": 1, "variant": 1, "granulated_data": 1}).limit(1000)
        
        # create a new list of dicts, with the font_info and glyphs_data expanded
        new_data = []
        for font in fonts:
            new_font = font['granulated_data']['font_info']

            # add the family and variant to the new dict
            new_font['family'] = font['family']
            new_font['variant'] = font['variant']

            # for each feature in glyphs_data, take the mean and std
            glyph_data = font['granulated_data']['glyphs_data']
            for feature in glyph_data:
                new_font[feature + '_mean'] = glyph_data[feature]['mean']
                new_font[feature + '_std'] = glyph_data[feature]['std']
            new_data.append(new_font)

        clustering_data = pd.DataFrame(new_data)
        clustering_data.to_csv('means_df.csv', index=False)

        # upload the data to mongo
        hook = MongoHook(mongo_conn_id='mongo_default')
        client = hook.get_conn()
        db = client['FontsFramework']
        collection = db['clustering_data']
        collection.drop()

        records = json.loads(clustering_data.T.to_json()).values()
        collection.insert_many(records)


    if False:
        notebook_task = PapermillOperator(
            task_id="clustering_notebook",
            input_nb="include/notebooks/kmeans.ipynb",
            output_nb="include/out-{{ execution_date }}.ipynb",
            parameters={"execution_date": "{{ execution_date }}",
                    "data_path": "means_df.csv"}
        )
    
    prepare_clustering_data()