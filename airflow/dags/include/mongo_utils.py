from airflow.providers.mongo.hooks.mongo import MongoHook
from pymongo.collection import Collection

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