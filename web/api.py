from flask import Flask, jsonify
import meeting_analysis
import utils
from dbclient import DbClient
from pymongo import MongoClient
import exceptions

app = Flask(__name__)

app.config.update(
    MONGODB_HOST = 'mongo',
    MONGODB_PORT = '27017',
    MONGODB_DB = 'processed_meetings',
)

dbclient = DbClient(MongoClient("mongo", 27017).processed_meetings)


def _no_data_response(msg, *args):
    """
    Generates a json response object with a given msg 
    and optional string formatting args
    """
    return jsonify({ "error": msg.format(args) }), 503

def _responsify(payload):
    """
    return a response with the payload
    """
    return jsonify({ "data": payload })


@app.route('/meetings/', methods=['GET'])
def get_meetings_meta():
    """
    Return the metadata for each meeting in the system 
    """
    # query all
    meetings_meta = dbclient.query("meta", "*")
    if not meetings_meta:
        return _no_data_response(
            "No meetings have been processed yet",
            )
    return _responsify(meetings_meta)

@app.route('/meetings/<meeting_key>/', methods=['GET'])
def get_single_meeting_meta(meeting_key):
    """
    Return the metadata for a specific meeting in the system 
    """
    query = {"meeting_key": meeting_key}
    meeting_meta = dbclient.query("meta", query)
    if not meeting_meta:
        return _no_data_response(
            "No meetings matching the meeting_key {} have been processed yet", 
            meeting_key)

    return _responsify(meeting_meta[0])

@app.route('/meetings/<meeting_key>/time/', methods=['GET'])
def get_meeting_speaking_time(meeting_key):
    """
    Returns the breakdown of speaking time for each user in the given meeting in seconds
    """
    query = {"meeting_key": meeting_key}
    events = dbclient.query("data", query)
    speaking_time = meeting_analysis.speaking_time(events)
    if not speaking_time:
        return _no_data_response("No speaking events for key {}", meeting_key)

    return _responsify(speaking_time)

@app.route('/meetings/<meeting_key>/turns/', methods=['GET'])
def get_meeting_speaking_turns(meeting_key):
    """
    Returns the breakdown of speaking turns for each user in the given meeting 
    """
    query = {"meeting_key": meeting_key}
    events = dbclient.query("data", query)
    speaking_turns = meeting_analysis.speaking_turns(events)
    if not speaking_turns:
        return _no_data_response("No speaking events for key {}", meeting_key)

    return _responsify(speaking_turns)

@app.route('/meetings/<meeting_key>/prompting/', methods=['GET'])
def get_meeting_prompting(meeting_key):
    """
    Return who follows whom in a meetings
    """
    query = {"meeting_key": meeting_key}
    events = dbclient.query("data", query)
    prompting = meeting_analysis.prompting(events)    
    if not prompting:
        return _no_data_response("No speaking events for key {}", meeting_key)
    
    return _responsify(prompting)

@app.route('/participants/', methods=['GET'])
def get_participants():
    """
    Return the list of all participants in all meetings
    """
    results = utils.query_table(mongo.meeting_meta, query)
    if not results:
        return _no_data_response("No meetings have been processed")

    participants = [ele["participants"] for ele in results]
    flatten = lambda l: [item for sublist in l for item in sublist]
    return _responsify({ "participants": flatten(participants) })

    

if __name__ == "__main__":
    app.run(host="0.0.0.0")
