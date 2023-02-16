from airflow import DAG

from airflow.decorators import task, task_group
from airflow.providers.mongo.hooks.mongo import MongoHook
from include.mongo_utils import get_ufo_collection
from include.data_enrichment import granulate_data
from include.data_utils.json_to_ufo import glyph_json_to_Glyph, glyph_to_svg_path
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

    # task to enrich the data
    @task()
    def granulate_fonts(**context):
        ufo_collection = get_ufo_collection("FontsFramework", "UFOs")
        for i in range(context["params"]["max_fonts_per_task"]):
            print(f"iteration {i}...")
            font_ids = \
                list(ufo_collection.find({"granulated_data": {"$exists": False}})\
                .limit(5))

            for ufo in font_ids:
                print(f"Enriching {ufo['family']} {ufo['variant']}...")
                font_info, glyphs_stats = granulate_data(ufo)
                # update mongo
                ufo_collection.update_one({"_id": ufo["_id"]}, {"$set": {"granulated_data" : {"font_info": font_info, "glyphs_data": glyphs_stats.to_dict()}}})

    @task()
    def convert_to_svg(**context):
        ufo_collection = get_ufo_collection("FontsFramework", "UFOs")
        for i in range(context["params"]["max_fonts_per_task"]):
            print(f"iteration {i}...")
            font_ids = \
                list(ufo_collection.find({"glyphs_svg": {"$exists": False}})\
                .limit(5))

            for ufo in font_ids:
                print(f"Converting {ufo['family']} {ufo['variant']}...")
                unitsPerEm = ufo["data"]["fontinfo_plist"]["unitsPerEm"]
                glyphs_svgs = {}
                for glif_name, glyph_json in ufo["data"]["glyphs"].items():
                    print(f"Converting {glif_name}...")
                    print(glyph_json)
                    glyph = glyph_json_to_Glyph(glyph_json)
                    try:
                        svg = glyph_to_svg_path(glyph, unitsPerEm)
                        glyphs_svgs[glif_name] = svg
                    except Exception as e:
                        print(f"Error converting {glif_name}...")
                        print(e)
                # update mongo
                ufo_collection.update_one({"_id": ufo["_id"]}, {"$set": {"glyphs_svg" : glyphs_svgs}})
                    
    #granulate_fonts()
    convert_to_svg()