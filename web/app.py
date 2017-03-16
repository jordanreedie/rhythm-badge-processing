from flask import Flask, jsonify
import meeting_analysis
import utils
from pymongo import MongoClient
import exceptions

app = Flask(__name__)

app.config.update(
    MONGODB_HOST = 'mongo',
    MONGODB_PORT = '27017',
    MONGODB_DB = 'processed_meetings',
)

mongo = MongoClient("mongo", 27017).processed_meetings

def array_to_json(arr, key): #TODO testing
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

def _no_data_response(msg, *args): #TODO testing
    """
    Generates a json response object with a given msg 
    and optional string formatting args
    """
    return jsonify({ "response": msg.format(args) })


@app.route('/', methods=['GET'])
def get_projects(): #TODO testing
    """
    Returns the list of the keys of the projects that have processed meetings 
    """
    projects = [doc['project_key'] for doc in mongo.meeting_meta.find()]
    return jsonify({ "projects": list(set(projects))})

@app.route('/<project_key>/meetings', methods=['GET'])
def get_meetings_meta(project_key): #TODO testing
    """
    Return the metadata for each meeting in the system 
    """
    query = { "project_key": project_key }
    meetings_meta = utils.query_table(mongo.meeting_meta, query)
    if not meetings_meta:
        return _no_data_response(
            "No meetings have been processed for project with key {}",
            project_key)

    return jsonify(array_to_json(meetings_meta, "meeting_key"))

@app.route('/<project_key>/meetings/<meeting_key>', methods=['GET'])
def get_single_meeting_meta(project_key, meeting_key): #TODO testing
    """
    Return the metadata for a specific meeting in the system 
    """
    query = {"project_key": project_key, "meeting_key": meeting_key}
    meeting_meta = utils.query_table(mongo.meeting_meta, query)
    if not meeting_meta:
        return _no_data_response(
            "No meetings matching the meeting_key {} exist under project {}", 
            meeting_key, project_key)

    return jsonify({
        "metadata": array_to_json(meeting_meta, "meeting_key")
    })

@app.route('/<project_key>/meetings/<meeting_key>/time', methods=['GET'])
def get_meeting_speaking_time(project_key, meeting_key): #TODO testing
    """
    Returns the breakdown of speaking time for each user in the given meeting in seconds
    """
    query = {"project_key": project_key, "meeting_key": meeting_key}
    speaking_time = meeting_analysis.speaking_time(mongo, query)
    if not speaking_time:
        return _no_data_response("No speaking events for key {}", meeting_key)

    return jsonify(speaking_time)

@app.route('/<project_key>/meetings/<meeting_key>/turns', methods=['GET'])
def get_meeting_speaking_turns(project_key, meeting_key): #TODO testing
    """
    Returns the breakdown of speaking turns for each user in the given meeting 
    """
    query = {"project_key": project_key, "meeting_key": meeting_key}
    speaking_turns = meeting_analysis.speaking_turns(mongo, query)
    if not speaking_turns:
        return _no_data_response("No speaking events for key {}", meeting_key)

    return jsonify(speaking_turns)

@app.route('/<project_key>/meetings/<meeting_key>/prompting', methods=['GET'])
def get_meeting_prompting(project_key, meeting_key): #TODO testing
    """
    Return who follows whom in a meetings
    """
    query = {"project_key": project_key, "meeting_key": meeting_key}
    prompting = meeting_analysis.prompting(mongo, query)    
    if not prompting:
        return _no_data_response("No speaking events for key {}", meeting_key)
    
    return jsonify(prompting)


if __name__ == "__main__":
        app.run(host="0.0.0.0")
