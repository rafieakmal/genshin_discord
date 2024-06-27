from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
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
            cls._instance.client = AsyncIOMotorClient(
                connection_string)
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
        result = await collection.insert_one(document)
        return result

    async def find_one(self, collection_name, query):
        """
        Find one document from the collection
        """
        collection = await self.get_collection(collection_name)
        result = await collection.find_one(query)
        return result

    async def find(self, collection_name, query):
        """
        Find all documents from the collection using a callback
        """
        collection = await self.get_collection(collection_name)
        cursor = collection.find(query)
        documents = []
        async for document in cursor:
            documents.append(document)
        return documents

    async def update_one(self, collection_name, query, update):
        """
        Update one document from the collection
        """
        collection = await self.get_collection(collection_name)
        result = await collection.update_one(query, {'$set': update})
        return result

    async def delete_one(self, collection_name, query):
        """
        Delete one document from the collection
        """
        collection = await self.get_collection(collection_name)
        result = await collection.delete_one(query)
        return result
    
    async def delete_many(self, collection_name, query):
        """
        Delete many documents from the collection
        """
        collection = await self.get_collection(collection_name)
        result = await collection.delete_many(query)
        return result

    async def delete_all(self, collection_name):
        """
        Delete all documents from the collection
        """
        collection = await self.get_collection(collection_name)
        result = await collection.delete_many({})
        return result

    async def get_staffs(self):
        """
        Get all staffs from the database using a callback
        """
        return await self.find("staffs", {})
    
    async def get_staffs_in_server(self, server_id):
        """
        Get all staffs from the database in a specific server using a callback
        """
        staff_ids = await self.find("staffs", {"server_id": server_id})
        staff_user_ids = [staff['user_id'] for staff in staff_ids]
        return staff_user_ids
