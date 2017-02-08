

from openbadge_analysis.core import *

import time
from data_collection.web_connection import WebConnection
import settings
import pandas
import matplotlib.pyplot as plt
from data_manipulation import df_stitched_to_events
from datastore import DataStore


if __name__ == "__main__":

    # we want to loop forever

    # how do we know what project to use?
    # settings for now
    conn = WebConnection()
    conn.connect(settings.project_key)
    datastore = DataStore()
    datastore.connect()
    while True:
        # check the remote data source for new data
        meeting_keys = conn.list_meeting_keys() 

        # this will keep track of the keys processed
        # we will get this value from the DB
        meetings_processed = datastore.list_meetings()

        new_meeting_keys = [meeting for meeting in meeting_keys if meeting not in meetings_processed]
       
        # if we get new data, process it
        for key in new_meeting_keys:
            raw_meeting_data = conn.read_meeting(key)
            metadata = conn.read_meeting_metadata(key)
            # convert to df
            df_meeting = json_sample2data(raw_meeting_data, True, True)
            df_meeting.metadata = metadata
            
            df_stitched = make_df_stitched(df_meeting)
            events =  df_stitched_to_events(key, df_stitched)
            
            #put in mongo
            datastore.store_meeting(metadata, events)

        # and now, we wait
        time.sleep(20)


