#!/usr/bin/env python

import unittest
#import httpretty
from data_collection.web_connection import WebConnection

class WebConnectionTest(unittest.TestCase):

    #@httpretty.activate
    def setUp(self):
        # Register the uris to mock
        # httpretty.register_uri(httpretty.GET, "http://api.yipit.com/v1/deals/",
        #        body='[{"title": "Test Deal"}]',
        #        content_type="application/json")
        self.conn = WebConnection()
        self.conn.connect("VLVYA95ZXS")


    def test_get_num_meetings(self):
        #TODO
        pass

    def test_read_meetings_metadata(self):
        #TODO
        print self.conn.read_meetings_metadata()
    def test_read_meeting(self):
        #TODO
        pass

if __name__ == '__main__':
        unittest.main()
