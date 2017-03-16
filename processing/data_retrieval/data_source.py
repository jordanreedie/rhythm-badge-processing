#!/usr/bin/env python
from abc import ABCMeta, abstractmethod

class DataSource:
    """
    This describes a standardized interface for connecting to a data source

    Includes necessary methods for interacting with the data
    """
    __metaclass__ = ABCMeta



    @abstractmethod
    def connect(self, project_key):
        """
        Establish a connection with the data source for the specified project

        :param project_key: the project key of the project to pull data from
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect from the data source and release any held resources
        """
        pass

    @abstractmethod
    def num_complete_meetings(self):
        """
        Return the number of complete meetings on the server 
        """
        pass

    @abstractmethod
    def read_meetings_metadata(self):
        """
        Get the metadata for all meetings on the server
        """
        pass

    @abstractmethod
    def read_meeting_metadata(self, meeting_key):
        """
        Get the metadata for a single meeting
        """
        pass

    @abstractmethod
    def read_meeting(self, meeting_key):
        """
        Reads data for a single meeting from the data source
        """
        pass

    @abstractmethod
    def list_meeting_keys(self):
        """
        Returns a list of the keys of all complete meetings
        """
        pass
