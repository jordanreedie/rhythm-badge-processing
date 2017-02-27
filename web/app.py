from flask import Flask, jsonify
from analysis.core import *
from pymongo import MongoClient
import exceptions

app = Flask(__name__)

app.config.update(
    MONGODB_HOST = 'mongo',
    MONGODB_PORT = '27017',
    MONGODB_DB = 'processed_meetings',
)

mongo = MongoClient("mongo", 27017).processed_meetings

def array_to_json(arr):
    json = {}
    for ele in arr:
        del[ele["_id"]]
        json[ele["key"]] = ele

    return json

def _get_speaking_events(project_key, meeting_key):
    """
    return the speaking events for the meeting matching the given
    project_key and meeting_key
    """

    # meeting keys are only guaranteed to be unique for a given project
    # so we use both keys to identify
    return [doc for doc in mongo.meeting_data.find({
        "meeting_key": meeting_key, 
        "project_key": project_key
    })]

@app.route('/', methods=['GET'])
def get_projects():
    """
    Returns the list of the keys of the projects that have processed meetings 
    """
    projects = [doc['project'] for doc in mongo.meeting_meta.find()]
    return jsonify({ "projects": list(set(projects))})

@app.route('/<project_key>/meetings', methods=['GET'])
def get_meetings_meta(project_key):
    """
    Return the metadata for each meeting in the system 
    """
    meetings_meta = [doc for doc in mongo.meeting_meta.find({ "project": project_key })]
    print type(meetings_meta)
    if not meetings_meta:
        return jsonify({ "response": "No meetings have been processed" })

    return jsonify(array_to_json(meetings_meta))

@app.route('/<project_key>/meetings/<meeting_key>', methods=['GET'])
def get_single_meetings_meta(project_key, meeting_key):
    """
    Return the metadata for a specific meeting in the system 
    """
    meeting_meta = [doc for doc in mongo.meeting_meta.find(
        {"project": project_key, "key": meeting_key}
    )]
    if not meeting_meta:
        return jsonify({ 
            "response": "No meetings matching the meeting_key {} exists under project {}"
            .format(meeting_key, project_key) 
        })

    return jsonify({
        "metadata": array_to_json(meeting_meta)
    })

@app.route('/<project_key>/meetings/<meeting_key>/time', methods=['GET'])
def get_speaking_time(project_key, meeting_key):
    # get all speaking events for this meeting key
    speaking_events = _get_speaking_events(project_key, meeting_key)
    if not speaking_events:
        return jsonify({ "response": "No meeting for for key {}".format(meeting_key) })

    return jsonify(speaking_time(speaking_events))

@app.route('/<project_key>/meetings/<meeting_key>/turns', methods=['GET'])
def get_speaking_turns(project_key, meeting_key):
    speaking_events = _get_speaking_events(project_key, meeting_key)
    if not speaking_events:
        return jsonify({ "response": "No meeting for for key {}".format(meeting_key) })

    return jsonify(speaking_turns(speaking_events))

@app.route('/<project_key>/meetings/<meeting_key>/prompting', methods=['GET'])
def get_prompting(project_key, meeting_key):
    speaking_events = _get_speaking_events(project_key, meeting_key)
    if not speaking_events:
        return jsonify({ "response": "No meeting for for key {}".format(meeting_key) })
    
    return jsonify(prompting(speaking_events))

@app.route('/<project_key>/participants', methods=['GET'])
def get_participants():
    participants = [doc["member_key"] for doc in mongo.meeting_data.find()] 
    return jsonify({"participants": list(set(participants))})

@app.route('/<project_key>/participants/<member_key>/turns', methods=['GET'])
def get_participant_time(project_key, member_key):
    speaking_events = _get_speaking_events(project_key, member_key)
    if not speaking_events:
        return jsonify({ "response": "No data for for participant {} in project {}"
            .format(member_key, project_key)})


    

# @app.route('/<project_key>/participants/<member_key>/turns', methods=['GET'])
# def get_participant_turns(member_key):

if __name__ == "__main__":
        app.run(host="0.0.0.0")


