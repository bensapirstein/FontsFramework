import pymongo
import yaml

try:
    from airflow.providers.mongo.hooks.mongo import MongoHook
except ImportError:
    pass
from pymongo.collection import Collection
from pymongo.server_api import ServerApi

def get_ufo_collection(db_name: str, collection_name: str) -> Collection:
    """
    Returns a MongoDB collection for UFO data.

    Parameters
    ----------
    db_name : str
        The name of the database.
    collection_name : str
        The name of the collection.

    Returns
    -------
    pymongo.collection.Collection
        A MongoDB collection.
    """
    hook = MongoHook(mongo_conn_id='mongo_default')
    client = hook.get_conn()
    db = client[db_name]
    collection = db[collection_name]
    collection.create_index([('family', 1), ('variant', 1)], unique=True)
    return collection



def pymongo_get_ufo_collection(db_name: str, collection_name: str, settings: dict) -> Collection:
    """
    Returns a MongoDB collection for UFO data, using connection information
    from the `airflow_settings.yaml` file.
    """

    conn_info = next(conn for conn in settings['connections'] if conn['conn_id'] == 'mongo_default')
    username = conn_info['conn_login']
    password = conn_info['conn_password']
    host = conn_info['conn_host']
    schema = conn_info['conn_schema']

    client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@{host}/{schema}", server_api=ServerApi('1'))
    db = client[db_name]
    collection = db[collection_name]
    collection.create_index([('family', 1), ('variant', 1)], unique=True)

    return collection

if __name__ == '__main__':
    with open('../../airflow_settings.yaml') as f:
        settings = yaml.safe_load(f)["airflow"]
    collection = pymongo_get_ufo_collection('FontsFramework', 'UFOs', settings)
    print(collection)
