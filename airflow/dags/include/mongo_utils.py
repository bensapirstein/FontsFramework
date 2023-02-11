from airflow.providers.mongo.hooks.mongo import MongoHook

def get_ufo_collection(db_name: str, collection_name: str):
    hook = MongoHook(mongo_conn_id='mongo_default')
    client = hook.get_conn()
    db = client[db_name]
    collection = db[collection_name]
    collection.create_index([('family', 1), ('variant', 1)], unique=True)
    return collection