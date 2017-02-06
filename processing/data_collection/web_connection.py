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
        self.request_base = settings.SERVER_URL
        self.project_key = project_key

    def num_complete_meetings(self):
        """
        Returns the number of complete meetings on the server
        """
        metadata = self.read_meetings_metadata()
        return len(metadata)


    def _get_metadata(self, meeting_data):
        meeting = {}
        meeting["uuid"] = meeting_data["metadata"]["data"]["uuid"]
        meeting["start_time"] = meeting_data["metadata"]["data"]["start_time"]
        meeting["is_complete"] = meeting_data["metadata"]["is_complete"]
        meeting["members"] = meeting_data["metadata"]["members"]
        return meeting

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
        print json_resp["meetings"]
        for meeting_key in json_resp["meetings"]:
            meeting_data = json_resp["meetings"][meeting_key]
            meeting_metadata.append(self._get_metadata(meeting_data))

        return meeting_metadata

    def read_meeting_metadata(self, meeting_key):
        api_endpoint = "/{}/meetings/{}".format(self.project_key, meeting_key)
        url = self.request_base + api_endpoint
        headers = self._generate_headers("False")
        resp = requests.get(url, headers=headers)
                
        if resp.status_code != 200:
            #TODO
            print "error! status code: {}".format(resp.status_code)
        

        json_resp = json.loads(resp.text)
        
        meeting_data = json_resp["meetings"][meeting_key]
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

        return json_resp["meetings"]["meeting_key"]["chunks"]
        
