#!/usr/bin/env python
import requests
import json
import settings
from data_source import DataSource

class WebConnection(DataSource):
    """
    Connects to the OpenBadge-Server via Rest API
    to collect data
    """

    def _generate_headers(self, get_file=False):
        return { 
            "x-appkey": settings.APPKEY,
            "x-get-file": get_file
        }

    def connect(self, project_key):
        """
        Perform any necessary setup for connecting to the data source
        """
        self.request_base = settings.SERVER_URL
        self.project_key = project_key

    def disconnect(self)
        """
        Disconnect from the data source and release any held resources
        """
        # we don't actually have to do anything here since it's all stateless
        pass

    def num_complete_meetings(self):
        """
        Returns the number of complete meetings on the server
        """
        metadata = self.read_meetings_metadata()
        return len(metadata)


    def _get_metadata(self, meeting_data):
        """
        Internal method for converting the meeting object returned from the
        django server API to a more conveniently formatted one

        :param meeting_data: the meeting object returned from the server
        """
        meeting = {}
        meeting["uuid"] = meeting_data["metadata"]["data"]["uuid"]
        meeting["start_time"] = meeting_data["metadata"]["data"]["start_time"]
        meeting["is_complete"] = meeting_data["metadata"]["is_complete"]
        meeting["members"] = meeting_data["metadata"]["members"]
        meeting["key"] = meeting_data["metadata"]["key"]
        meeting["project"] = meeting_data["metadata"]["project"]
        meeting["end_time"] = meeting_data["metadata"]["end_time"]
        return meeting

    def list_meeting_keys(self):
        """
        Returns a list of the keys of all complete meetings
        """

        meetings_meta = self.read_meetings_metadata()
        meeting_keys = []
        for meeting in meetings_meta:
            meeting_keys.append(meeting["key"])
    
        return meeting_keys

    def read_meetings_metadata(self):
        """
        Get the metadata for all meetings
        """
        api_endpoint = "/{}/meetings".format(self.project_key)
        headers = self._generate_headers("false")
        url = self.request_base + api_endpoint
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            #TODO
            print "error! status code: {}".format(resp.status_code)
            
        json_resp = json.loads(resp.text)
        
        meeting_metadata = []
        for meeting_key in json_resp["meetings"]:
            meeting_data = json_resp["meetings"][meeting_key]
            meeting_metadata.append(self._get_metadata(meeting_data))

        return meeting_metadata

    def read_meeting_metadata(self, meeting_key):
        """
        Get the metadata for a single meeting
        
        :param meeting_key: key of the desired meeting
        """
        api_endpoint = "/{}/meetings/{}".format(self.project_key, meeting_key)
        url = self.request_base + api_endpoint
        headers = self._generate_headers("False")
        resp = requests.get(url, headers=headers)
                
        if resp.status_code != 200:
            #TODO
            print "error! status code: {}".format(resp.status_code)
        

        json_resp = json.loads(resp.text)
        
        meeting_data = json_resp[meeting_key]
        return self._get_metadata(meeting_data)

    def read_meeting(self, meeting_key):
        """
        Get the data for a single meeting
        
        :param meeting_key: key of the meeting to grab
        """

        api_endpoint = "/{}/meetings/{}".format(self.project_key, meeting_key)
        url = self.request_base + api_endpoint
        headers = self._generate_headers("true")
        resp = requests.get(url, headers=headers)
                
        if resp.status_code != 200:
            #TODO
            print "error! status code: {}".format(resp.status_code)

        json_resp = json.loads(resp.text)
        
        batched_data = []
        for chunk in json_resp[meeting_key]["chunks"]:
            if "audio" in chunk["type"]:
                batched_data.append(chunk["data"])

        return batched_data
        
