#!/usr/bin/env python
from abc import ABCMeta, abstractmethod

class DataSource:
    __metaclass__ = ABCMeta

    """
    This describes a standardized interface for connecting to a data source
    """


    @abstractmethod
    def connect(self):
        """
        Establish a connection with the data source
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

