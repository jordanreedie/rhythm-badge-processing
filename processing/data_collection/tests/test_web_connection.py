#!/usr/bin/env python

import unittest
import httpretty

class WebConnectionTest(unittest.TestCase):

    @httpretty.activate
    def setUp(self):
        # Register the uris to mock
        httpretty.register_uri(httpretty.GET, "http://api.yipit.com/v1/deals/",
               body='[{"title": "Test Deal"}]',
               content_type="application/json")


    def test_get_num_meetings(self):
        #TODO
        pass

    def test_read_meetings_metadata(self):
        #TODO
        pass

    def test_read_meeting(self):
        #TODO
        pass
