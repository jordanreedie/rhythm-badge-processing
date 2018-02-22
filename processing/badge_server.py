#!/usr/bin/env python
import requests
import json
import settings

class BadgeServer():
    """
    Connects to the OpenBadge-Server via Rest API
    to retrieve badge data
    """
    def __init__(self, project_key):
        """
        Perform any necessary setup for connecting to the data source
        """
        self.request_base = settings.SERVER_URL
        self.project_key = project_key
        self.badge_name_map = {}

    def _generate_headers(self, get_file="false"):
        return { 
            "x-appkey": settings.APPKEY,
            "x-get-file": get_file,
            "x-hub-uuid": settings.HUB_UUID
        }

    def _make_request(self, endpoint, use_project_key=True, request_file="false"):
        # because the badge server api is funky af
        if use_project_key:
            api_endpoint = "/{}/{}".format(self.project_key, endpoint)
        else:
            api_endpoint = "/{}/".format(endpoint)

        headers = self._generate_headers(request_file)
        url = self.request_base + api_endpoint
        resp = requests.get(url, headers=headers)

        return resp

    def _request_badge_name(self, key):
        """
        Request badge name from server

        Returns the name as a String
        """
        resp = self._make_request("badges/{}".format(key), use_project_key=False)
        if resp.status_code != 200:
            print "error! status code: {}".format(resp.status_code)
            print resp.text
            return 

        json_resp = json.loads(resp.text)
        return json_resp["name"]


    def _get_metadata(self, meeting_data):
        """
        Internal method for extracting the metadata from the meeting 
        object returned from the django server API 

        :param meeting_data: the meeting object returned from the server
        """
        meeting = {}
        meeting["uuid"] = meeting_data["metadata"]["data"]["uuid"]
        meeting["start_time"] = float(meeting_data["metadata"]["data"]["start_time"])
        meeting["is_complete"] = meeting_data["metadata"]["is_complete"]
        meeting["description"] = meeting_data["metadata"]["data"]["description"]
        meeting["participants"] = meeting_data["metadata"]["members"]
        meeting["meeting_key"] = meeting_data["metadata"]["key"]
        meeting["project_key"] = meeting_data["metadata"]["project"]
        if meeting["is_complete"]:
            meeting["end_time"] = float(meeting_data["metadata"]["end_time"])

        return meeting

    def num_complete_meetings(self):
        """
        Returns the number of complete meetings on the server
        """
        metadata = self.read_meetings_metadata()
        return len(metadata)

    def list_meeting_keys(self):
        """
        Returns a dict of the mapping of keys to uuids of all meetings
        """
        meetings_meta = self.read_meetings_metadata()
        # we want a dict of meeting_key : meeting_uuid
        meeting_uuids = { meeting["meeting_key"]: meeting["uuid"] for meeting in meetings_meta }
        return meeting_uuids

    def read_meetings_metadata(self):
        """
        Get the metadata for all meetings
        """
        resp = self._make_request("meetings")

        if resp.status_code != 200:
            #TODO
            print "error! status code: {}".format(resp.status_code)
            print resp.text
            return []

        json_resp = json.loads(resp.text)
        
        meeting_metadata = []
        for meeting_key in json_resp["meetings"]:
            meeting_data = json_resp["meetings"][meeting_key]
            meeting_metadata.append(self._get_metadata(meeting_data))

        return meeting_metadata

    def read_meeting_metadata(self, meeting_key, meeting_uuid):
        """
        Get the metadata for a single meeting
        
        :param meeting_key: key of the desired meeting
        """
        resp = self._make_request("meetings/{}".format(meeting_uuid))
                
        if resp.status_code != 200:
            #TODO
            print "error reading meeting {}! status code: {}".format(meeting_key, resp.status_code)
            print resp.text
            return []
        

        json_resp = json.loads(resp.text)
        meeting_data = json_resp[meeting_key]
        return self._get_metadata(meeting_data)

    def read_meeting(self, meeting_key, meeting_uuid):
        """
        Get the data for a single meeting
        
        :param meeting_key: key of the meeting to grab
        """
        resp = self._make_request("meetings/{}".format(meeting_uuid), request_file="true")
                
        if resp.status_code != 200:
            #TODO
            print "error! status code: {}".format(resp.status_code)
            return []

        json_resp = json.loads(resp.text)
        
        batched_data = []
        for chunk in json_resp[meeting_key]["chunks"]:
            if "audio" in chunk["type"]:
                batched_data.append(chunk["data"])

        return batched_data
        
    def get_participant_name(self, key):
        """
        Look up the participant name in our internal map or request from server
        and update internal mapping if not exists

        Returns the name as a String
        """
        if key in self.badge_name_map:
            return self.badge_name_map[key]
        else:
            self.badge_name_map[key] = self._request_badge_name(key)
            return self.badge_name_map[key]
