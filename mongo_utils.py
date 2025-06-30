from pymongo import MongoClient
import pandas as pd

def connect_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["cdr_logs"]
    return db

def insert_dataframe_to_collection(db, collection_name, df):
    if not df.empty:
        db[collection_name].insert_many(df.to_dict("records"))

def list_collections(db):
    return db.list_collection_names()

def load_collection_as_df(db, collection_name):
    data = list(db[collection_name].find({}, {"_id": 0}))
    return pd.DataFrame(data)
