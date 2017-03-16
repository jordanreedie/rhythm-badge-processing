#!/usr/bin/env python

def increment(json_obj, key, amt):
    """
    Increment the value at <key> in <json_obj> by <amt> if it exists
    otherwise set it to one
    """
    json_obj[key] = json_obj[key] + amt if key in json_obj  else amt

def query_table(table, query):
    """
    """
    return [doc for doc in table.find(query)]

def get_meta(db, query):
    """
    Get the meta for each meeting matching the query in the db
    """
    return [doc for doc in db.meeting_meta.find(query)]

def get_speaking_events(db, query):
    return query_table(db.meeting_data, query)
