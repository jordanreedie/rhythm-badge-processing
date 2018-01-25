import pymongo

class DbClient():
    
    def __init__(self, db):
        self.db = db

    def get_meeting_meta(self, meeting_key):
        """
        return meeting metadata for specified meeting key
        OR all meetings, if meeting_key = *
        """
        query = meeting_key if meeting_key == "*" else {"meeting_key": meeting_key}
        meeting_meta = dbclient.query("meta", query)
        return meeting_meta

    def get_meeting_data(self, meeting_key):
        query = {"meeting_key": meeting_key}
        data = dbclient.query("data", query)
        return data

    def _get_table(table):
        query_table = None
        if table == "meta":
            query_table = "meeting_meta" 
        elif table == "data":
            query_table = "meeting_data"
        elif query_table == "participants":
            query_table = "participants"
        else:
            #TODO error
            pass
        return query_table

    def query(self, table, query):

        query_table = _get_table(table)

        if query == "*":
            docs = [doc for doc in self.db[query_table].find()]
        else:
            docs = [doc for doc in self.db[query_table].find(query)]

        for doc in docs:
            del doc["_id"]
    
        return docs

    def count(self, table, query):
        query_table = _get_table(table)
        if query == "*":
            count = [doc for doc in self.db[query_table].count()]
        else:
            count = [doc for doc in self.db[query_table].count(query)]

        return count

