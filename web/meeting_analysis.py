#!/usr/bin/env python
from utils import get_speaking_events, increment 


def _speaking_time(speaking_events): #TODO testing
    """
    Takes a list of speaking events from a meeting
    Returns a json object indicating the total speaking time
    for each member
    """
    time = {}

    for event in speaking_events:
        key = event["member_key"]
        duration = int(event["speaking_end"]) - int(event["speaking_start"])
        increment(time, key, duration)
        
    return time

def speaking_time(db, query):
    """
    """
    speaking_events = get_speaking_events(db, query)
    return _speaking_time(speaking_events)

def _prompting(speaking_events): #TODO testing
    """
    Take a list of speaking events from a meeting
    Returns a json object of how many times a participant
    spoke after each member. 

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
        # probably shouldnt happen
        return {}

    sorted_events = sorted(speaking_events, key=lambda event: int(event['speaking_end']))
    # need to keep track of who spoke last
    last_speaker = sorted_events[0]["member_key"]
    # skip the first event since we already grabbed the first speaker
    for event in sorted_events[1:]:
        current_speaker = event["member_key"]
        following = prompts[last_speaker] if last_speaker in prompts else {}
        increment(following, current_speaker, 1)
        prompts[last_speaker] = following
        last_speaker = current_speaker

    return prompts

def prompting(db, query):
    speaking_events = get_speaking_events(db, query)
    return _prompting(speaking_events)

def _speaking_turns(speaking_events): #TODO testing
    """
    Takes a list of speaking events from a meeting
    Returns a json object indicating the number of turns taken
    for each member
    """
    turns = {}

    for event in speaking_events:
        key = event["member_key"]
        increment(turns, key, 1)
        
    return turns

def speaking_turns(db, query):
    speaking_events = get_speaking_events(db, query)
    return _speaking_turns(speaking_events)
