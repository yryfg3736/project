from pymongo import MongoClient
import os

def get_collection(collection_name):
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_uri)
    db = client['tweets_database']
    return db[collection_name]