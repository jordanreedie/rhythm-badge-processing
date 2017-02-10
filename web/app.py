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

@app.route('/<meeting_key>/time', methods=['GET'])
def get_speaking_time(meeting_key):
    # get all speaking events for this meeting key
    speaking_events = [doc for doc in mongo.meeting_data.find({"meeting_key": meeting_key})]
    if not speaking_events:
        return jsonify({ "response": "No meeting for for key {}".format(meeting_key) })
    return jsonify(speaking_time(speaking_events))

@app.route('/<meeting_key>/turns', methods=['GET'])
def get_speaking_turns(meeting_key):
    speaking_events = [doc for doc in mongo.meeting_data.find({"meeting_key": meeting_key})]
    if not speaking_events:
        return jsonify({ "response": "No meeting for for key {}".format(meeting_key) })
    return jsonify(speaking_turns(speaking_events))

@app.route('/<meeting_key>/prompting', methods=['GET'])
def get_prompting(meeting_key):
    speaking_events = [doc for doc in mongo.meeting_data.find({"meeting_key": meeting_key})]
    if not speaking_events:
        return jsonify({ "response": "No meeting for for key {}".format(meeting_key) })
    return jsonify(prompting(speaking_events))


if __name__ == "__main__":
        app.run(host="0.0.0.0")


