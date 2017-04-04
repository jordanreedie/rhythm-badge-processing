import pymongo

class DbClient():
    
    def __init__(self, db):
        self.db = db

    def query(self, table, query):
        if table == "meta":
            query_table = "meeting_meta" 
        else:
            query_table = "meeting_data"

        if query == "*":
            docs = [doc for doc in self.db[query_table].find()]
        else:
            docs = [doc for doc in self.db[query_table].find(query)]

        for doc in docs:
            del doc["_id"]
    
        return docs
