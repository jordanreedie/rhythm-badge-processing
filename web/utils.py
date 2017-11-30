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

def array_to_json(arr, key):
    """ 
    convert an array of meeting objects to a single json object
    with each meeting in the object identified by its key

    :param arr: the array to convert
    :param key: the name of the field you want to use for the key,
      e.g. with key "meeting_key"
       [ { "meeting_key": "245XG34", ... } ] -> { "245XG34": <obj> } 
    """
    json = {}
    for ele in arr:
        # the _id field breaks stuff so we delete it
        # we don't do anything with it anyway
        del[ele["_id"]]
        json[ele[key]] = ele

    return json

def no_data_response(msg, *args):
    """
    Generates a json response object with a given msg 
    and optional string formatting args
    """
    return jsonify({ "error": msg.format(args) }), 503

def responsify(payload):
    """
    return a response with the payload
    """
    return jsonify({ "data": payload })

def get_participants(meeting_key):
    query = {"meeting_key": meeting_key}
    meeting_meta = dbclient.query("meta", query)
    participants = []
    if meeting_meta:
        participants = meeting_meta[0]["participants"]
    return participants 
