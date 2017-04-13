#!/usr/bin/env python
import utils


def chunked_speaking_time(speaking_events, n=5):
    """
    Takes a list of speaking events from a meeting and splits it into
    n-minute speaking time breakdowns
    
    :param speaking_events: speaking events JSON
    :param n: how long each chunk is, in minutes
    """
    time = [{}]
    chunk_begin = speaking_events[0]["speaking_start"]
    chunk_len = n * seconds
    chunk_end = chunk_begin + chunk_len
    chunk_counter = 0
    for event in speaking_events:
        key = event["participant_key"]
        if speaking_end < chunk_end:
            # the entire speaking event is within the confines of this chunk
            #TODO DRY       
            duration = int(event["speaking_end"]) - int(event["speaking_start"])
            utils.increment(time[chunk_counter], key, duration)
        elif speaking_start < chunk_end:
            # the speaking event is split across two chunks
            # we will need to split the duration accordingly
            
            curr_chunk_duration = chunk_end - event["speaking_start"]
            utils.increment(time[chunk_counter], key, curr_chunk_duration)
            next_chunk_duration = event["speaking_end"] - chunk_end
            #TODO DRY       
            chunk_counter += 1
            chunk_begin = chunk_end + 1
            chunk_end = chunk_begin + chunk_len
            
            time.append({})
            utils.increment(time[chunk_counter], key, next_chunk_duration)
        else:
            # the event is entirely in the next chunk
            #TODO DRY       
            chunk_counter += 1
            chunk_begin = chunk_end + 1
            chunk_end = chunk_begin + chunk_len
            
            time.append({})
            utils.increment(time[chunk_counter], key, next_chunk_duration)

            #TODO DRY       

            duration = int(event["speaking_end"]) - int(event["speaking_start"])
            utils.increment(time[chunk_counter], key, duration)



        
    return time


def speaking_time(speaking_events): 
    """
    Takes a list of speaking events from a meeting
    Returns a json object indicating the total speaking time in seconds
    for each participant
    """
    time = {}

    for event in speaking_events:
        key = event["participant_key"]
        duration = int(event["speaking_end"]) - int(event["speaking_start"])
        utils.increment(time, key, duration)
        
    return time

def prompting(speaking_events): 
    """
    Take a list of speaking events from a meeting
    Returns a json object of how many times a participant
    spoke after each participant. 

    {
      <key>: {
         <key>: x,
         <key>: y,
         ...
      },
      ...
    }
    """
    prompts = {}
    if not speaking_events:
        #TODO raise exception?
        # this means we were given an empty list of events
        # probably shouldnt happen ever
        return {}

    sorted_events = sorted(speaking_events, key=lambda event: int(event['speaking_end']))
    # need to keep track of who spoke last
    last_speaker = sorted_events[0]["participant_key"]
    # skip the first event since we already grabbed the first speaker
    for event in sorted_events[1:]:
        current_speaker = event["participant_key"]
        following = prompts[last_speaker] if last_speaker in prompts else {}
        utils.increment(following, current_speaker, 1)
        prompts[last_speaker] = following
        last_speaker = current_speaker

    return prompts

def speaking_turns(speaking_events):
    """
    Takes a list of speaking events from a meeting
    Returns a json object indicating the number of turns taken
    for each participant
    """
    turns = {}

    for event in speaking_events:
        key = event["participant_key"]
        utils.increment(turns, key, 1)
        
    return turns

