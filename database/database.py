import pymongo
import certifi
import config

class Database:
    _instance = None

    def __new__(cls):
        """
        Create a new instance of the database
        """
        if cls._instance is None:
            connection_string = config.mongo
            cls._instance = super().__new__(cls)
            cls._instance.client = pymongo.MongoClient(
                connection_string, tlsCAFile=certifi.where())
            cls._instance.db = cls._instance.client['genshinindo']
        return cls._instance

    async def get_collection(self, collection_name):
        """
        Get the collection from the database
        """
        return self._instance.db[collection_name]

    async def insert_one(self, collection_name, document):
        """
        Insert one document into the collection
        """
        collection = await self.get_collection(collection_name)
        return collection.insert_one(document)

    async def find_one(self, collection_name, query):
        """
        Find one document from the collection
        """
        collection = await self.get_collection(collection_name)
        return collection.find_one(query)

    async def find(self, collection_name, query):
        """
        Find all documents from the collection
        """
        collection = await self.get_collection(collection_name)
        return collection.find(query)

    async def update_one(self, collection_name, query, update):
        """
        Update one document from the collection
        """
        collection = await self.get_collection(collection_name)
        return collection.update_one(query, update)

    async def delete_one(self, collection_name, query):
        """
        Delete one document from the collection
        """
        collection = await self.get_collection(collection_name)
        return collection.delete_one(query)
    
    async def delete_many(self, collection_name, query):
        """
        Delete many documents from the collection
        """
        collection = await self.get_collection(collection_name)
        return collection.delete_many(query)

    async def delete_all(self, collection_name):
        """
        Delete all documents from the collection
        """
        collection = await self.get_collection(collection_name)
        return collection.delete_many({})
    
    async def get_staffs(self):
        """
        Get all staffs from the database
        """
        return await self.find("staffs", {})
    
    async def get_staffs_in_server(self, server_id):
        """
        Get all staffs from the database in a specific server
        """
        staff_ids = await self.find("staffs", {"server_id": server_id})
        return [staff['user_id'] for staff in staff_ids]
