from airflow import DAG

from airflow.decorators import task, task_group
from airflow.providers.mongo.hooks.mongo import MongoHook
from include.mongo_utils import get_ufo_collection
from include.data_enrichment import enrich_data
from datetime import datetime

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
    "data_enrichment_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    params={
        "max_fonts_per_task": 10,
        "num_parallel_tasks": 1,
    }
    ) as dag:

    # task to fetch from mongo fonts that weren't enriched yet
    @task()
    def get_fonts_from_mongo(**context):
        # get ufo from mongo
        ufo_collection = get_ufo_collection("FontsFramework", "UFOs")
        # get fonts that weren't enriched yet
        font_ids = list(ufo_collection.find({"glyph_aggregated_data": {"$exists": False}}, {"family": 1, "variant": 1}))
        print("#############################################")
        print(font_ids)
        return {"font_ids": font_ids}
    

    # task to enrich the data
    @task()
    def enrich_fonts(**context):
        ufo_collection = get_ufo_collection("FontsFramework", "UFOs")
        font_ids = \
            list(ufo_collection.find({"granulated_data": {"$exists": False}})\
            .limit(context["params"]["max_fonts_per_task"]))

        for ufo in font_ids:
            print(f"Enriching {ufo['family']} {ufo['variant']}...")
            font_info, glyphs_stats = enrich_data(ufo)
            # update mongo
            ufo_collection.update_one({"_id": ufo["_id"]}, {"$set": {"granulated_data" : {"font_info": font_info, "glyphs_data": glyphs_stats.to_dict()}}})

    # task to update the mongo collection
    @task()
    def update_mongo(font):
        aggregated_data = None
        # update mongo
        ufo_collection = get_ufo_collection("FontsFramework", "UFOs")
        ufo_collection.update_one({"_id": font["_id"]}, {"$set": {"data.lib_plist.glyph_aggregated_data": aggregated_data}})
            
    enrich_fonts()