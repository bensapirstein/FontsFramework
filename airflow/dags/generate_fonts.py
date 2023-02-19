from airflow import DAG
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime

from airflow.decorators import task, task_group
from airflow.providers.mongo.hooks.mongo import MongoHook

from include.mongo_utils import get_ufo_collection
from include.data_utils.ufo_to_ttf import ufo_to_ttf
from include.data_utils.json_to_ufo import json_to_ufo
from include.data_utils.ufo_to_json import ufo_to_json
from include.data_generation import get_font_combinations, create_unified_font
from bson.objectid import ObjectId
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 0,
}

with DAG(
        "generate_fonts", 
        start_date=datetime(2023, 1, 1),
        schedule_interval="@daily", 
        catchup=False,
        params={
            'num_fonts' : 2,
            'font_folder' : "generated_fonts",
            'action' : 'generate_multilingual_fonts.get_multilingual_ufos',
            'multilingual_subsets' : ['latin', 'arabic', 'hebrew'],
            'format' : 'ttf',
            'num_parallel_tasks' : 1,
        }
    ) as dag:

    @task_group
    def generate_multilingual_fonts():
        ufo_collection = get_ufo_collection("FontsFramework", "UFOs")

        @task
        def get_multilingual_ufos(**context):
            params = context['params']
            subsets = params['multilingual_subsets']
            # fetch ufos from mongo that support different languages
            # given the list of languages, fetch ufos that together support all the languages
            # pass the list of ufos to the next task
            fonts_by_subset = {}
            for subset in subsets:
                ufos = ufo_collection.find({"subsets": subset}, {"_id": 1})
                fonts_by_subset[subset] = [str(ufo["_id"]) for ufo in ufos]
                # pass the list of ufos supporting the given language to the next task
            
            combinations = get_font_combinations(subsets, fonts_by_subset, params['num_fonts'])
            # pass the list of font combinations to the next task
            context['ti'].xcom_push(key='combinations', value=combinations)
        
        @task
        def download_relevant_ufos(**context):
            params = context['params']
            combinations = context['ti'].xcom_pull(key='combinations')
            # download all fonts that are relevant to the font combinations
            for combination in combinations:
                for ufo_id in combination.values():
                    # download the ufo
                    ufo = ufo_collection.find_one({"_id": ObjectId(ufo_id)})
                    # drop the id field
                    ufo_path = f"{params['font_folder']}/{ufo_id}.ufo"
                    # save the ufo to the given path
                    json_to_ufo(ufo["data"], ufo_path)


        @task
        def unite_ufos(**context):
            params = context['params']
            combinations = context['ti'].xcom_pull(key='combinations')
            # unite the ufos in each combination to create a multilingual font
            result_ufos = []
            for combination in combinations:
                ufos = [f"{params['font_folder']}/{ufo_id}.ufo" for ufo_id in combination.values()]
                # create a unified font
                unified_font = create_unified_font(ufos)
                # save the unified font to the given path
                result_path = f"{params['font_folder']}/{unified_font.info.familyName}-{unified_font.info.styleName}.ufo"
                unified_font.save(result_path)
                result_ufos.append(result_path)

            context['ti'].xcom_push(key='result_ufos', value=result_ufos)

        get_multilingual_ufos() >> download_relevant_ufos() >> unite_ufos()

    @task
    def generate_shuffled_fonts():
        # generate shuffled fonts
        pass

    @task
    def generate_variable_fonts():
        # generate variable fonts
        pass

    @task
    def generate_custom_fonts():
        # generate custom fonts
        pass

    @task 
    def upload_ufo(**context):
        ufo_collection = get_ufo_collection("FontsFramework", "generatedUFOs")
        params = context['params']
        results = context['ti'].xcom_pull(key='result_ufos')
        print(results)
        # upload ufo to mongo
        result_ids = []
        for result in results:
            ufo_json = ufo_to_json(result)
            print(ufo_json)
            response = ufo_collection.insert_one(\
                {\
                    'family': ufo_json['fontinfo_plist']['familyName'], \
                    'variant': ufo_json['fontinfo_plist']['styleName'], \
                    'data': ufo_json, 'subsets': params['multilingual_subsets'] \
                })
            result_ids.append(str(response.inserted_id))

            # TODO: deduce the subsets from the unified ufos

        print("Done uploading ufo")
        context['ti'].xcom_push(key='result_ids', value=result_ids)

    @task.branch
    def choose_action(**context):
        return context['params']['action']
        
    @task
    def woff():
        # generate woff
        pass

    @task
    def woff2():
        # generate woff2
        pass

    @task
    def ttf(**context):
        params = context['params']
        results = context['ti'].xcom_pull(key='result_ufos')
        result_ids = context['ti'].xcom_pull(key='result_ids')
        ufo_collection = get_ufo_collection("FontsFramework", "generatedUFOs")

        # generate ttf
        for i, result in enumerate(results):
            ttf_path = f"{params['font_folder']}/{result.split('/')[-1].split('.')[0]}.ttf"
            ufo_to_ttf(result, ttf_path)

            #update mongo with the ttf file
            pass

    @task
    def otf():
        # generate otf
        pass        

    @task
    def upload_formatted_font():
        # upload fonts to mongo
        pass

    @task.branch
    def choose_format():
        return "ttf"

    # Define the Dag structure
    branching = choose_action()
    join = EmptyOperator(
        task_id="join",
        trigger_rule="none_failed_min_one_success"
    )
    join2 = EmptyOperator(
        task_id="join2",
        trigger_rule="none_failed_min_one_success"
    )
    branching >> generate_multilingual_fonts() >> join
    branching >> generate_shuffled_fonts() >> join
    branching >> generate_variable_fonts() >> join
    branching >> generate_custom_fonts() >> join
    join >> upload_ufo() >> choose_format() >> [woff(), woff2(), ttf(), otf()] >> join2 >> upload_formatted_font()
