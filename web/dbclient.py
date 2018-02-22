import pymongo

class DbClient():
    
    def __init__(self, db):
        self.db = db

    def get_most_recent_meeting(self):
        docs = self.db["meetings"].find().sort("end_time", -1).limit(1) 
        mtg = [doc for doc in docs][0]
        del mtg["_id"]
        return mtg

    def get_meeting_meta(self, meeting_key):
        """
        return meeting metadata for specified meeting key
        OR all meetings, if meeting_key = *
        """
        query = meeting_key if meeting_key == "*" else {"meeting_key": meeting_key}
        meeting_meta = self.query("meta", query)
        return meeting_meta

    def get_meeting_data(self, meeting_key):
        query = {"meeting_key": meeting_key}
        data = self.query("data", query)
        return data

    def _get_table(self, table):
        query_table = None
        if table == "meta":
            query_table = "meetings" 
        elif table == "data":
            query_table = "speaking_events"
        elif table == "participants":
            query_table = "participants"
        else:
            #TODO error
            pass
        return query_table

    def query(self, table, query):

        query_table = self._get_table(table)

        if query == "*":
            docs = [doc for doc in self.db[query_table].find()]
        else:
            docs = [doc for doc in self.db[query_table].find(query)]

        for doc in docs:
            del doc["_id"]
    
        return docs

    def count(self, table, query):
        query_table = self._get_table(table)
        if query == "*":
            count = self.db[query_table].count()
        else:
            count = self.db[query_table].count(query)

        return count

