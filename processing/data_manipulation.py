#!/usr/bin/env python

import pandas
import numpy
import time

def _index_to_ts(index):
    """
    Takes a pandas dataframe timestamp index and converts it to unix time
    """
    return time.mktime(index.timetuple())


def df_stitched_to_events(meeting_key, project_key, df): 
    """
    Takes a pandas dataframe of stitched is_speaking values
    and returns a list speaking events of the format:

    [{ 
        meeting_key: <str>,
        participant_key: <str>,
        speaking_start: <timestamp>,
        speaking_end: <timestamp>,
        project_key: <str>
    }, ...]
    """

    # this is p gross BUT
    # we have to rename the columns of the dataframe in case they start with a number
    # because it's possible they are invalid python identifiers
    # this gives us trouble with named tuples
    df.rename(columns = lambda col: "C_" + col, inplace=True)

    # initialize a dict to keep track of whether each participant 
    # was speaking in the previous row,
    # and when they started
    participants = {}
    for column in list(df):
        participants[column] = {
            "was_speaking": "false",
            "start_time": 0
        }

    speaking_events = []
    # df.itertuples() yields named tuples, format: (index, <col1>=<val1>, etc.)
    for row in df.itertuples():
        index = row[0]
        for column in participants:
            is_speaking = getattr(row, column)
            was_speaking = participants[column]["was_speaking"] == "true"

            # a transition from false -> true of was_speaking -> is_speaking
            # marks the start of a speaking event
            if is_speaking and not was_speaking:
                participants[column]["was_speaking"] = "true"
                participants[column]["start_time"] = _index_to_ts(index)
            # a transition from true -> false of is_speaking -> was_speaking
            # marks the end of a speaking event
            elif not is_speaking and was_speaking:
                participants[column]["was_speaking"] = "false"
                speaking_events.append({
                    "meeting_key": meeting_key,
                    "project_key": project_key,
                    # remove the C_ prefix to column
                    "participant_key": column[2:],
                    "speaking_start": participants[column]["start_time"],
                    "speaking_end": _index_to_ts(index)
                })
                
    # we need to check if a participant was speaking 
    # until the very very end of the meeting,
    # otherwise we'll miss their speaking event
    for column in participants:
        if participants[column]["was_speaking"] == "true":
           speaking_events.append({
                    "meeting_key": meeting_key,
                    "project_key": project_key,
                    # remove the C_ prefix to column
                    "participant_key": column[2:],
                    "speaking_start": participants[column]["start_time"],
                    "speaking_end": _index_to_ts(df.index.max())
           })
        
    #re-rename the columns
    # C_<colname> -> <colname>
    df.rename(columns = lambda col: col[2:], inplace=True)

    return speaking_events

def merge_turns(speaking_events, max_length=2, min_length=1):
    """
    If a participant speaks, takes a break < max_length ms, and speaks again
    (with no other participants speaking), that should be one turn

    AND

    if a participants speaks for < min_length, it is not counted as a turn
    """
    if not speaking_events:
        return []
    events = sorted(speaking_events, key=lambda e: e["speaking_start"])
    merged_turns = []
    prev_turn = events[0]
    merged_turns.append(prev_turn)
    for turn in events[1:]:
        # if the previous and current speaker are the same
        if (turn["participant_key"] == prev_turn["participant_key"] and 
            (turn["speaking_start"] - prev_turn["speaking_end"]) < max_length):
            merged_turns[-1]["speaking_end"] = turn["speaking_end"]
        elif turn_len(turn) < min_length:
            # do not include the turn in the list of events
            print "tiny len"
            continue
        else:
            merged_turns.append(turn)

        prev_turn = turn

    return merged_turns

def turn_len(turn):
    return turn["speaking_end"] - turn["speaking_start"]
