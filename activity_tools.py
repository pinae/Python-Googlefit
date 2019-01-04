#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from datetime import datetime, timedelta
from google_fit_activity_types import activity_map


def trunc_datetime(dt):
    return datetime(year=dt.year, month=dt.month, day=dt.day)


def ceil_datetime(dt):
    return datetime(year=(dt + timedelta(days=1)).year,
                    month=(dt + timedelta(days=1)).month,
                    day=(dt + timedelta(days=1)).day)


def activities_to_days(activities):
    if len(activities) <= 0:
        return []
    days = []
    current_day = []
    if ceil_datetime(activities[0]['start_time']) < activities[0]['end_time']:
        current_cursor = ceil_datetime(activities[0]['start_time'])
    else:
        current_cursor = activities[0]['start_time']
    current_index = 0
    activity = activities[current_index].copy()
    while activity is not None and activity['end_time'] > current_cursor:
        if activity['start_time'] > ceil_datetime(current_cursor):
            days.append(current_day)
            current_day = []
        if activity['start_time'] < current_cursor:
            activity['start_time'] = current_cursor
        while activity['end_time'] > ceil_datetime(current_cursor):
            cut_activity = activity.copy()
            cut_activity['end_time'] = ceil_datetime(current_cursor)
            activity['start_time'] = cut_activity['end_time']
            current_day.append(cut_activity)
            days.append(current_day)
            current_day = []
            current_cursor = cut_activity['end_time']
        current_day.append(activity)
        current_cursor = activity['end_time']
        current_index += 1
        if current_index < len(activities):
            activity = activities[current_index].copy()
        else:
            activity = None
    days.append(current_day)
    return days


def fill_day_with_unknown(day):
    full_day = []
    if day[0]['start_time'] < trunc_datetime(day[0]['start_time']):
        full_day.append({
            'activity': "Unknown (unable to detect activity)*", 'activity_no': 4,
            'start_time': trunc_datetime(day[0]['start_time']),
            'end_time': day[0]['start_time']
        })
    for i, activity in enumerate(day):
        full_day.append(activity.copy())
        if i + 1 < len(day):
            next_time = day[i + 1]['start_time']
        elif ceil_datetime(activity['end_time']) - activity['end_time'] < timedelta(days=1):
            next_time = ceil_datetime(activity['end_time'])
        else:
            next_time = activity['end_time']
        if next_time > activity['end_time']:
            full_day.append({
                'activity': "Unknown (unable to detect activity)*", 'activity_no': 4,
                'start_time': activity['end_time'],
                'end_time': next_time
            })
    return full_day


def create_activity_priority_map():
    automatic_activities = []
    sleep_activities = []
    unknown_activities = [
        "Unknown (unable to detect activity)*",
        "Tilting (sudden device gravity change)*",
        "Still (not moving)*"]
    for i in activity_map:
        if activity_map[i].endswith("*"):
            automatic_activities.append(activity_map[i])
        if activity_map[i].find("sleep") > 0 or activity_map[i] == "Sleeping":
            sleep_activities.append(activity_map[i])
    activity_priority_map = {}
    for i in activity_map:
        if activity_map[i] in unknown_activities:
            activity_priority_map[i] = unknown_activities.index(activity_map[i])
        elif activity_map[i] in automatic_activities:
            activity_priority_map[i] = automatic_activities.index(activity_map[i]) + len(unknown_activities)
        elif activity_map[i].find("sleep") > 0 or activity_map[i] == "Sleeping":
            activity_priority_map[i] = sleep_activities.index(activity_map[i]) + \
                                       len(unknown_activities) + len(automatic_activities)
        else:
            activity_priority_map[i] = i + len(unknown_activities) + len(automatic_activities) + len(sleep_activities)
    return activity_priority_map


def clean_activities(activities):
    activity_priority_map = create_activity_priority_map()
    act = activities.copy()
    act.sort(key=lambda x: activity_priority_map[x['activity_no']])
    cleaned_activities = []
    for activity in reversed(act):
        activity_slices = [activity]
        for ea in cleaned_activities:
            for i, sl in enumerate(activity_slices):
                if sl['start_time'] >= ea['start_time'] and sl['end_time'] <= ea['end_time']:
                    activity_slices.pop(i)
                elif (sl['end_time'] > ea['start_time'] and sl['start_time'] < ea['end_time']) or (
                        sl['start_time'] < ea['end_time'] and sl['end_time'] > ea['start_time']):
                    if sl['start_time'] >= ea['start_time'] and sl['end_time'] > ea['end_time']:
                        sl['start_time'] = ea['end_time']
                    elif sl['start_time'] < ea['start_time'] and sl['end_time'] <= ea['end_time']:
                        sl['end_time'] = ea['start_time']
                    elif sl['start_time'] < ea['start_time'] and sl['end_time'] > ea['end_time']:
                        new_sl = sl.copy()
                        sl['end_time'] = ea['start_time']
                        new_sl['start_time'] = ea['end_time']
                        activity_slices.append(new_sl)
        cleaned_activities += activity_slices
    cleaned_activities.sort(key=lambda x: x['start_time'], reverse=False)
    return cleaned_activities
