
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
        cursor = self.db["meetings"].find({})
        return [doc["meeting_key"] for doc in cursor if doc["is_complete"]]
        
    def store_meeting(self, meeting_meta, speaking_events):
        """
        Store a meeting in the database
        """
        if meeting_meta:
            self.store_meta(meeting_meta)

        if speaking_events:
            self.db["speaking_events"].insert_many(speaking_events)

    def store_meta(self, meeting_meta):
        meeting_key = meeting_meta["meeting_key"]
        if not self.get_meeting_meta(meeting_key):
            self.db["meetings"].insert_one(meeting_meta)
        else:
            self.db["meetings"].replace_one({"meeting_key": meeting_key}, meeting_meta)

    def get_meeting_meta(self, meeting_key):
        cursor =  self.db["meetings"].find({"meeting_key": meeting_key})
        return [doc for doc in cursor]

    def get_meeting_data(self, meeting_key):
        cursor =  self.db["speaking_events"].find({"meeting_key": meeting_key})
        return [doc for doc in cursor]

    def store_participant_meeting(self, participant_key, participant_name, meeting_key):
        query = { "participant_key": participant_key }
        data =  { 
            "$addToSet": { "meeting_key": meeting_key },
            "$setOnInsert": { "name": participant_name}
        }

        self.db["participants"].update(query, data, True)
    
    def list_participants(self):
        return [part["meeting_key"] for part in self.db["participants"].find()]

    
