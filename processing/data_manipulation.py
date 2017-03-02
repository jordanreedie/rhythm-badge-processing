#!/usr/bin/env python

import pandas
import time

def _index_to_ts(index):#TODO testing
    """
    Takes a pandas dataframe timestamp index and converts it to unix time
    """
    return time.mktime(index.timetuple())


def df_stitched_to_events(meeting_key, project_key, df): #TODO testing
    """
    Takes a pandas dataframe of stitched is_speaking values
    and returns a list speaking events of the format:

    [{ 
        meeting_key: <str>,
        member_key: <str>,
        speaking_start: <timestamp>
        speaking_end: <timestamp>
        project_key: <str>
    }, etc.]
    """

    # we have to rename the columns of the dataframe in case they start with a number
    # because it's possible they are invalid python identifiers
    # this gives us trouble with named tuples
    df.rename(columns = lambda col: "C_" + col, inplace=True)

    # initialize a dict to keep track of whether each member 
    # was speaking in the previous row,
    # and when they started
    members = {}
    for column in list(df):
        members[column] = {
            "was_speaking": "false",
            "start_time": 0
        }

    speaking_events = []
    # df.itertuples() yields named tuples, format: (index, <col1>=<val1>, etc.)
    for row in df.itertuples():
        index = row[0]
        for column in members:
            is_speaking = getattr(row, column)
            was_speaking = members[column]["was_speaking"] == "true"

            # a transition from false -> true of was_speaking -> is_speaking
            # marks the start of a speaking event
            if is_speaking and not was_speaking:
                members[column]["was_speaking"] = "true"
                members[column]["start_time"] = _index_to_ts(index)

            # a transition from true -> false of is_speaking -> was_speaking
            # marks the end of a speaking event
            elif not is_speaking and was_speaking:
                members[column]["was_speaking"] = "false"
                speaking_events.append({
                    "meeting_key": meeting_key,
                    "project_key": project_key,
                    # remove the C_ prefix to column
                    "member_key": column[2:],
                    "speaking_start": members[column]["start_time"],
                    "speaking_end": _index_to_ts(index)
                })
                
    # we need to check if a participant was speaking 
    # until the very very end of the meeting,
    # otherwise we'll miss their speaking event
    for column in members:
        if members[column]["was_speaking"] == "true":
           speaking_events.append({
                    "meeting_key": meeting_key,
                    "project_key": project_key,
                    # remove the C_ prefix to column
                    "member_key": column[2:],
                    "speaking_start": members[column]["start_time"],
                    "speaking_end": _index_to_ts(df.index.max())
           })
        
    #re-rename the columns
    # C_<colname> -> <colname>
    df.rename(columns = lambda col: col[2:], inplace=True)

    return speaking_events
