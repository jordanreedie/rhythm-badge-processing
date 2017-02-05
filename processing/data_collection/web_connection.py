#!/usr/bin/env python
import requests
import json
import settings

class WebConnection(DataSource):
    """
    Connects to the OpenBadge-Server via Rest API
    to collect data
    """


    project_key = ""

    def _generate_headers(self, get_file=False):
        return { 
            "x-appkey": settings.APPKEY,
            "x-get-file": get_file
        }

    def connect(self):
        self.request_base = settings.SERVER_URL

    def get_num_meetings(self):
        """
        Returns the number of complete meetings on the server
        """
        metadata = self.read_meetings_metadata()
        return len(metadata)


    def read_meetings_metadata(self):
        """
        Get the metadata for all meetings
        """
        api_endpoint = "/{}/meetings".format(project_key)
        headers = self._generate_headers(False)
        url = self.request_base + api_endpoint
        resp = requests.get(url, header=headers)
        if resp.status_code != 200:
            #TODO
            
        json_resp = json.loads(resp.text)
        
        meeting_metadata = []
        for meeting_data in json_resp.meetings:
            meeting = {}
            meeting["uuid"] = meeting_data.metadata.data.uuid
            meeting["start_time"] = meeting_data.metadata.data.start_time
            #TODO must add is_complete to server response
            meeting["is_complete"] = meeting_data.metadata.data.is_complete
            meeting["members"] = meeting_data.metadata.data.members
            meeting_metadata.append(meeting)    
    
        return meeting_metadata

    def read_meetings(self):
        api_endpoint = "/{}/meetings".format(project_key)
        headers = self._generate_headers(True)
        url = self.request_base + api_endpoint
        resp = requests.get(url, header=headers)
        
        if resp.status_code != 200:
            #TODO
            
        json_resp = json.loads(resp.text)

    def read_meeting(self, meeting_key):
        """
        Get the data for a single meeting
        
        :param meeting_key: key of the meeting to grab
        """

        api_endpoint = "/{}/meetings/{}".format(project_key, meeting_key)
        url = self.request_base + api_endpoint
        resp = requests.get(url, header=self.headers)
                
        if resp.status_code != 200:
            #TODO

        json_resp = json.loads(resp.text)
    
        return json_resp
        





