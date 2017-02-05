#!/usr/bin/env python
from abc import ABCMeta, abstractmethod

class DataSource(metaclass=ABCMeta):
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
    def get_num_meetings(self):
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
    def read(self):
        """
        Reads data from the data source
        """
        pass

    @abstractmethod
    def has_new_data(self):
        """
        Does the data source have new data?
        """
        pass
