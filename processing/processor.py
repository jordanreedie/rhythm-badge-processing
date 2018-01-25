from openbadge_analysis.core import json_sample2data, make_df_stitched

import time
import settings
import pandas
import matplotlib.pyplot as plt
import data_manipulation
from datastore import DataStore
from badge_server import BadgeServer


def data_to_events(raw_data, metadata):
    """
    convert raw meeting data to speaking events 
    """
    # convert to df 
    df_meeting = json_sample2data(raw_meeting_data, True, True)
    df_meeting.metadata = metadata
    df_stitched = make_df_stitched(df_meeting)
    project_key = metadata["project_key"] 
    meeting_key = metadata["meeting_key"]
    # convert df to speaking events for storage
    speaking_events = data_manipulation.df_stitched_to_events(meeting_key, project_key, df_stitched)

    # merge any events that are close enough to be considered one turn
    merged_events = data_manipulation.merge_turns(speaking_events)

    return merged_events

def update_participant_meetings(metadata, datastore):
    participants = metadata["participants"]
    meeting_key = metadata["meeting_key"]

    for participant in participants:
        datastore.store_participant_meeting(participant, meeting_key)

def process_meeting(conn, datastore, key):
    """
    process the meeting from <conn> identified by <key> and store it in <datastore>
    """

    raw_meeting_data = conn.read_meeting(key)
    metadata = conn.read_meeting_metadata(key)
    # if the meeting is incomplete or didnt contain any data
    if not metadata["is_complete"] or not raw_meeting_data:
        # store the metadata and get out
        datastore.store_meta(metadata)
        return

    speaking_events = data_to_events(raw_meeting_data, metadata) 
    # store the newly processed data in the db
    datastore.store_meeting(metadata, merged_events)

    # TODO perfom some basic analysis and store in the db
    # analysis is currently done on a per-request basis. 

    update_participants(metadata, datastore)

def process(conn, datastore):
    """
    check <conn> for new meeting data
    if it has new data, process it and store it in <datastore>
    """
    # check the remote data source for new data
    meeting_keys = conn.list_meeting_keys() 

    meetings_processed = datastore.list_meetings()
    
    new_meeting_keys = [meeting for meeting in meeting_keys if meeting not in meetings_processed]

    # if we get new data, process it
    for key in new_meeting_keys:
        process_meeting(conn, datastore, key)


if __name__ == "__main__":
    # how do we know what project to use?
    # we can probably assume we want to process all of them?
    # settings for now
    badge_server = BadgeServer(settings.project_key)
    datastore = DataStore()
    datastore.connect()

    # we want to loop forever
    while True:
        process(badge_server, datastore)
        # we dont expect new meetings to be occurring particularly quickly
        # so this just limits responsiveness after a meeting has occurred
        time.sleep(settings.SLEEP_TIME)
