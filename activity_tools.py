#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from datetime import datetime, timedelta


def trunc_datetime(dt):
    return datetime(year=dt.year, month=dt.month, day=dt.day)


def ceil_datetime(dt):
    return datetime(year=(dt + timedelta(days=1)).year,
                    month=(dt + timedelta(days=1)).month,
                    day=(dt + timedelta(days=1)).day)


def activities_to_days(activities):
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
