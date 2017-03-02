from openbadge_analysis.core import *

import time
from data_collection.web_connection import WebConnection
import settings
import pandas
import matplotlib.pyplot as plt
from data_manipulation import df_stitched_to_events
from datastore import DataStore




def process_meeting(conn, datastore, key):
    """
    process the meeting from <conn> identified by <key> and store it in <datastore>
    """

    raw_meeting_data = conn.read_meeting(key)
    metadata = conn.read_meeting_metadata(key)
    # convert to df
    df_meeting = json_sample2data(raw_meeting_data, True, True)
    df_meeting.metadata = metadata
    project_key = metadata["project"] 
    df_stitched = make_df_stitched(df_meeting)
    events =  df_stitched_to_events(key, project_key, df_stitched)

    # store the newly processed data in the db
    datastore.store_meeting(metadata, events)

def process(conn, datastore):
    # check the remote data source for new data
    meeting_keys = conn.list_meeting_keys() 

    meetings_processed = datastore.list_meetings()
    new_meeting_keys = [meeting for meeting in meeting_keys if meeting not in meetings_processed]

    # if we get new data, process it
    for key in new_meeting_keys:
        process_meeting(conn, datastore, key)


if __name__ == "__main__":
    # how long to sleep after each loop
    SLEEP_TIME = 20 #seconds

    # how do we know what project to use?
    # we can probably assume we want to process all of them?
    # settings for now
    conn = WebConnection()
    conn.connect(settings.project_key)
    datastore = DataStore()
    datastore.connect()

    # we want to loop forever
    while True:
        process(conn, datastore)
        time.sleep(SLEEP_TIME)
