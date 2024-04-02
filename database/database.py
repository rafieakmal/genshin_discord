import pymongo, certifi

class Database:
    def __init__(self, connection_string):
        self.client = pymongo.MongoClient(connection_string, tlsCAFile=certifi.where())
        self.db = self.client['genshinindo']

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def insert_one(self, collection_name, document):
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)

    def find_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def find(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find(query)

    def update_one(self, collection_name, query, update):
        collection = self.get_collection(collection_name)
        return collection.update_one(query, update)

    def delete_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)
    
    def delete_many(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.delete_many(query)

    def delete_all(self, collection_name):
        collection = self.get_collection(collection_name)
        return collection.delete_many({})