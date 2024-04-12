import pymongo, certifi
import config

# import the package globally

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            connection_string = config.mongo
            cls._instance = super().__new__(cls)
            cls._instance.client = pymongo.MongoClient(
                connection_string, tlsCAFile=certifi.where())
            cls._instance.db = cls._instance.client['genshinindo']
        return cls._instance

    def get_collection(self, collection_name):
        return self._instance.db[collection_name]

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