
import os
from pymongo import MongoClient
class DataStore(object):
    """
    Manage, access, and update the processed data database
    """
    
    def connect(self):
        """
        establish a connection with the mongo DB
        """
        self.client = MongoClient("mongo", 27017)
        self.db = self.client.processed_meetings

    def list_meetings(self):
        """
        Return a list of the keys of the processed meetings
        """
        cursor = self.db["meeting_meta"].find({})
        return [doc["key"] for doc in cursor]
        
    def store_meeting(self, meeting_meta, speaking_events):
        """
        Store a meeting in the database
        """
        self.db["meeting_meta"].insert_one(meeting_meta)
        self.db["meeting_data"].insert_many(speaking_events)

    def get_meeting_data(self, meeting_key):
        cursor =  self.db["meeting_data"].find({"key": meeting_key})
        return [doc for doc in cursor]
