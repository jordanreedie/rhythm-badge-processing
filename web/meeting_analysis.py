#!/usr/bin/env python
import utils


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

