from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
import meeting_analysis
import utils
from dbclient import DbClient
from pymongo import MongoClient
import exceptions
from settings import AUTH_TOKEN
import os
import urllib

app = Flask(__name__)

app.config.update(
    MONGODB_HOST = 'mongo',
    MONGODB_PORT = '27017',
    MONGODB_DB = 'processed_meetings',
)
CORS(app)

dbclient = DbClient(MongoClient("mongo", 27017).processed_meetings)

@app.before_request
def verify_token():
    # TODO make this a little more secure
    if "/health" in request.url:
        return None
    url_token = request.args.get('token') 
    if not url_token:
        return jsonify({ "error": "Valid Token Required" }), 401
    elif url_token != AUTH_TOKEN:
        return jsonify({ "error": "Invalid Token Provided" }), 401
    else:
        return None

@app.route('/health', methods=['GET'])
def health():
    return utils.responsify("OK!")

###################################
######## MEETING ENDPOINTS ########
###################################

@app.route('/meetings/', methods=['GET'])
def get_meetings():
    """
    Return the metadata for each meeting in the system 
    """
    # query all
    meetings_meta = dbclient.get_meeting_meta("*")
    if not meetings_meta:
        return utils.no_data_response("No meetings have been processed yet")

    return utils.responsify(meetings_meta)

@app.route('/meetings/count/', methods=['GET'])
def get_num_meetings():
    """
    Return the total number of meetings
    """
    return utils.responsify(dbclient.count("meta", "*"))

@app.route('/meetings/recent/', methods=['GET'])
def get_recent_meeting():
    """
    Return the metadata for most recent meeting
    """

    meeting_meta = dbclient.get_most_recent_meeting()
    if not meeting_meta:
        return utils.no_data_response(
            "No meetings have been processed yet")

    return utils.responsify(meeting_meta)

@app.route('/meetings/meta/<meeting_key>/', methods=['GET'])
def get_single_meeting(meeting_key):
    """
    Return the metadata for a specific meeting in the system 
    """
    meeting_meta = dbclient.get_meeting_meta(meeting_key)
    if not meeting_meta:
        return utils.no_data_response(
            "No meetings matching the meeting_key {} have been processed yet", 
            meeting_key)

    return utils.responsify(meeting_meta[0])

@app.route('/meetings/time/<meeting_key>/', methods=['GET'])
def get_meeting_speaking_time(meeting_key):
    """
    Returns the breakdown of speaking time for each user in the given meeting in seconds
    """
    events = dbclient.get_meeting_data(meeting_key)
    if not events:
        return utils.no_data_response(
            "No meetings matching the meeting_key {} have been processed yet", 
            meeting_key)
    speaking_time = meeting_analysis.speaking_time(events)

    if not speaking_time:
        for part in _get_participants(meeting_key):
            speaking_time[part] = 0

    return utils.responsify(speaking_time)

@app.route('/meetings/turns/<meeting_key>/', methods=['GET'])
def get_meeting_speaking_turns(meeting_key):
    """
    Returns the breakdown of speaking turns for each user in the given meeting 
    """
    events = dbclient.get_meeting_data(meeting_key)
    if not events:
        return utils.no_data_response(
            "No meetings matching the meeting_key {} have been processed yet", 
            meeting_key)

    speaking_turns = meeting_analysis.speaking_turns(events)
    if not speaking_turns:
        for part in _get_participants(meeting_key):
            speaking_turns[part] = 0

    return utils.responsify(speaking_turns)

@app.route('/meetings/prompting/<meeting_key>/', methods=['GET'])
def get_meeting_prompting(meeting_key):
    """
    Return who follows whom in a meetings
    """
    events = dbclient.get_meeting_data(meeting_key)
    if not events:
        return utils.no_data_response("No speaking events for key {}", meeting_key)
    prompting = meeting_analysis.prompting(events)    
    
    return utils.responsify(prompting)

@app.route('/meetings/chunked_time/<meeting_key>/', methods=['GET'])
def get_chunked_time(meeting_key):
    """
    Return the breakdown of speaking time in n-minute chunks
    """
    events = dbclient.get_meeting_data(meeting_key)
    
    n = str(request.args.get('n', default=5))
    if not n.isdigit() or "." in n:
        return utils.no_data_response("Chunking value must be an integer!")

    chunks = meeting_analysis.chunked_speaking_time(events, int(n))

    return utils.responsify(chunks)

@app.route('/meetings/chunked_turns/<meeting_key>/', methods=['GET'])
def get_chunked_turns(meeting_key):
    """
    Return the breakdown of speaking turns in n-minute chunks
    """
    events = dbclient.get_meeting_data(meeting_key)
    
    n = str(request.args.get('n', default=5))
    if not n.isdigit() or "." in n:
        return utils.no_data_response("Chunking value must be an integer!")

    chunks = meeting_analysis.chunked_speaking_turns(events, int(n))

    return utils.responsify(chunks)

############################
## AGGREGATE MEETING DATA ##
############################
@app.route('/meetings/time/', methods=['GET'])
def get_total_minutes_spoken():
    start_time_agg = dbclient.db["speaking_events"].aggregate([
        {
            "$group": {
                "_id": None,
                "total": {
                    "$sum": "$speaking_start"
                }
            }
        }
    ])

    start_time_sum = list(start_time_agg)[0]["total"]
    end_time_agg = dbclient.db["speaking_events"].aggregate([
        {
            "$group": {
                "_id": None,
                "total": { 
                    "$sum": "$speaking_end"
                }
            }
        }
    ])


    end_time_sum = list(end_time_agg)[0]["total"]
    seconds_spoken = end_time_sum - start_time_sum

    return utils.responsify(int(seconds_spoken/60))

@app.route('/meetings/turns/', methods=['GET'])
def get_total_turns_taken():
    return utils.responsify(dbclient.count("data", "*"))

###################################
###### PARTICIPANT ENDPOINTS ######
###################################

@app.route('/participants/in_progress/<participant_key>/', methods=['GET'])
def get_in_progress(participant_key):
    """
    Return the meeting key of the in progress meeting for the given 
    participant, or null otherwise
    """
    query = { "participants": participant_key, "is_complete": False }
    meta = dbclient.query("meta", query)
    payload = None
    if meta:
        payload = meta[0]["meeting_key"]

    return utils.responsify(payload)

@app.route('/participants/count/', methods=['GET'])
def get_num_participants():
    """
    Return the total number of unique participants
    """
    return utils.responsify(dbclient.count("participants", "*"))

@app.route('/participants/speaking_time/<participant_key>/', methods=['GET'])
def get_participant_total_minutes(participant_key):
    """
    Return the total number of minutes spoken for a given participant
    """
    pass
        
@app.route('/participants/speaking_turns/<participant_key>/', methods=['GET'])
def get_participant_total_turns(participant_key):
    """
    Return the total number of turns taken for a given participant
    """
    pass

if __name__ == "__main__":
    app.run(host="0.0.0.0")
