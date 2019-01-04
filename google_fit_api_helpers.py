#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from google_fit_activity_types import activity_map
from datetime import datetime, timedelta


def extract_workout_data(raw_workouts):
    workouts = []
    for raw_data in raw_workouts:
        for activity in raw_data['point']:
            workout = {
                "activity": activity_map[activity['value'][0]['intVal']]
                if activity['value'][0]['intVal'] in activity_map.keys() else
                "unknown activity with no. " + str(activity['value'][0]['intVal']),
                "activity_no": activity['value'][0]['intVal'],
                "start_time": datetime.fromtimestamp(int(activity['startTimeNanos']) / 1000000000),
                "end_time": datetime.fromtimestamp(int(activity['endTimeNanos']) / 1000000000)
            }
            if 'originDataSourceId' in activity:
                workout["sourceId"] = activity['originDataSourceId']
            workouts.append(workout)
    return workouts


def merge_calories_expended_with_workouts(raw_calories_expended, workouts):
    for raw_data in raw_calories_expended:
        for point in raw_data['point']:
            calories_data_point = {
                "value": point['value'][0]['fpVal'],
                "start_time": datetime.fromtimestamp(int(point['startTimeNanos']) / 1000000000),
                "end_time": datetime.fromtimestamp(int(point['endTimeNanos']) / 1000000000)
            }
            # print("{:10.2f} kcal at {} - {}".format(calories_data_point['value'],
            #                                         calories_data_point['start_time'],
            #                                         calories_data_point['end_time']))
            for workout in workouts:
                if (timedelta(seconds=-1) < workout['start_time'] - calories_data_point['start_time'] <
                        timedelta(seconds=1) and timedelta(seconds=-1) <
                        workout['end_time'] - calories_data_point['end_time'] < timedelta(seconds=1)):
                    workout['calories'] = calories_data_point['value']
    return workouts
