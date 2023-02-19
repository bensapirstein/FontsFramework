from airflow import DAG

from airflow.decorators import task, task_group
from airflow.providers.mongo.hooks.mongo import MongoHook
from include.mongo_utils import get_ufo_collection
from include.data_granulation import granulate_data
from include.data_utils.json_to_ufo import json_to_ufo
from include.data_utils.glyph_utils import glyphs_to_svg_paths
from datetime import datetime
from bson import json_util
from bson.objectid import ObjectId
import json
import os

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

def parse_json(data):
    return json.loads(json_util.dumps(data))

with DAG(
    "data_enrichment",
    start_date=datetime(2023, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    params={
        "batch_size": 4,
    }
    ) as dag:

    @task_group
    def extract(n):
        ufo_collection = get_ufo_collection("FontsFramework", "UFOs")

        @task
        def get_font_ids(**context):
            # Get font ids of fonts that have not been enriched yet.
            # not enriched fonts are those that do not have the "granulated_data" field or "glyphs_svg" field
            # Limit the number of fonts to be processed in parallel
            font_ids = \
                list(ufo_collection.find({"$or": [{"granulated_data": {"$exists": False}}, {"glyphs_svg": {"$exists": False}}]}, {"_id": 1})\
                    .limit(n))

            # extract the font ids from the list of dicts
            font_ids = [str(font_id["_id"]) for font_id in font_ids]
            
            # pass the list of font ids to the next task
            context["ti"].xcom_push(key="font_ids", value=parse_json(font_ids))
        
        @task
        def download_ufo(i, **context):
            font_id = context["ti"].xcom_pull(key="font_ids", task_ids="extract.get_font_ids")[i]

            # download the ufo data from mongo for all font ids and save them to UFO file, then pass all file paths to the next task.
            # Perform one request to mongo to fetch all the data for all the fonts
            
            ufo = ufo_collection.find_one({"_id": ObjectId(font_id)}, {"data": 1, "family": 1, "variant": 1})

            # convert the json data to ufo
            ufo_path = f"/tmp/{ufo['family']}-{ufo['variant']}.ufo"
            json_to_ufo(ufo["data"], ufo_path)

            return ufo_path

        get_font_ids() >> [download_ufo.override(task_id=f"download_ufo_{i}")(i) for i in range(n)]

    @task_group
    def transform(n):
        ufo_collection = get_ufo_collection("FontsFramework", "UFOs")

        @task
        def convert_to_svg(i, **context):
            ufo_path = context["ti"].xcom_pull(key="return_value", task_ids=f"extract.download_ufo_{i}")
            ufo_id = context["ti"].xcom_pull(key="font_ids", task_ids="extract.get_font_ids")[i]

            # convert the glyphs to svg
            glyphs_svgs = glyphs_to_svg_paths(ufo_path)

            ufo_collection.update_one({"_id": ObjectId(ufo_id)}, {"$set": {"glyphs_svg" : glyphs_svgs}})

            # pass the svg paths to the next task
            context["ti"].xcom_push(key="glyphs_svgs", value=glyphs_svgs)

        @task
        def granulate_ufo(i, **context):
            ufo_path = context["ti"].xcom_pull(key="return_value", task_ids=f"extract.download_ufo_{i}")
            ufo_id = context["ti"].xcom_pull(key="font_ids", task_ids="extract.get_font_ids")[i]

            font_info, glyphs_stats = granulate_data(ufo_path)
            ufo_collection.update_one({"_id": ObjectId(ufo_id)}, {"$set": {"granulated_data" : {"font_info": font_info, "glyphs_data": glyphs_stats.to_dict()}}})

        [convert_to_svg.override(task_id=f"convert_to_svg_{i}")(i) >> granulate_ufo.override(task_id=f"granulate_ufo_{i}")(i) for i in range(n)]
            

    @task_group
    def load():
        @task
        def delete_ufos(**context):
            print(f"Deleting all ufo files")
            os.system(f"rm -rf /tmp/*.ufo")
        
        @task
        def update_mongo(**context):
            pass
                
            
        update_mongo() >> delete_ufos()
        
            
    n = dag.params["batch_size"]
    extract(n) >> transform(n) >> load()