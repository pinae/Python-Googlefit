#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from google_fit_activity_types import activity_map
from datetime import datetime, timedelta
import json
import os


def extract_workout_data(raw_workouts):
    workouts = []
    for raw_data in raw_workouts:
        for activity in raw_data['point']:
            workout = {
                "activity": activity_map[activity['value'][0]['intVal']]
                if activity['value'][0]['intVal'] in activity_map.keys() else
                "unknown activity with no. " + str(activity['value'][0]['intVal']),
                "activity_no": activity['value'][0]['intVal'],
                "dataSourceId": raw_data['dataSourceId'],
                "original_start_time": datetime.fromtimestamp(int(activity['startTimeNanos']) / 1000000000),
                "original_end_time": datetime.fromtimestamp(int(activity['endTimeNanos']) / 1000000000)
            }
            workout['start_time'] = workout['original_start_time']
            workout['end_time'] = workout['original_end_time']
            if 'originDataSourceId' in activity:
                workout["originDataSourceId"] = activity['originDataSourceId']
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
                    workout['caloriesDataSourceId'] = raw_data['dataSourceId']
    return workouts


def patch_raw_workouts_with_changed_activity(raw_workouts, raw_calories_expended, activity):
    changed_workout_data_source = None
    changed_calories_expended_data_source = None
    for raw_workout in raw_workouts:
        if raw_workout['dataSourceId'] == activity['dataSourceId']:
            changed_points = []
            for point in raw_workout['point']:
                new_point = point.copy()
                st = datetime.fromtimestamp(int(point['startTimeNanos']) / 1000000000)
                et = datetime.fromtimestamp(int(point['endTimeNanos']) / 1000000000)
                if (timedelta(seconds=-1) < st - activity['original_start_time'] < timedelta(seconds=1) and
                        timedelta(seconds=-1) < et - activity['original_end_time'] < timedelta(seconds=1)):
                    if (timedelta(seconds=-1) < st - activity['start_time'] < timedelta(seconds=1) or
                            timedelta(seconds=-1) < et - activity['end_time'] < timedelta(seconds=1) or
                            activity['activity_no'] != point['value'][0]['intVal']):
                        new_point['startTimeNanos'] = str(int(activity['start_time'].timestamp() * 1000000000))
                        new_point['endTimeNanos'] = str(int(activity['end_time'].timestamp() * 1000000000))
                        new_point['modifiedTimeMillis'] = str(int(datetime.now().timestamp() * 1000000000))
                        new_point['value'][0]['intVal'] = activity['activity_no']
                        changed_workout_data_source = raw_workout
                changed_points.append(new_point)
            raw_workout['point'] = changed_points
    for raw_calories_expended_item in raw_calories_expended:
        if 'caloriesDataSourceId' in activity and 'calories' in activity and (
                raw_calories_expended_item['dataSourceId'] == activity['caloriesDataSourceId']):
            changed_points = []
            for point in raw_calories_expended_item['point']:
                new_point = point.copy()
                st = datetime.fromtimestamp(int(point['startTimeNanos']) / 1000000000)
                et = datetime.fromtimestamp(int(point['endTimeNanos']) / 1000000000)
                if (timedelta(seconds=-1) < st - activity['original_start_time'] < timedelta(seconds=1) and
                        timedelta(seconds=-1) < et - activity['original_end_time'] < timedelta(seconds=1)):
                    if abs(point['value'][0]['fpVal'] - activity['calories']) > 0.01:
                        new_point['modifiedTimeMillis'] = str(int(datetime.now().timestamp() * 1000000000))
                        new_point['value'][0]['fpVal'] = activity['calories']
                        changed_calories_expended_data_source = raw_calories_expended_item
                changed_points.append(new_point)
            raw_calories_expended_item['point'] = changed_points
    return changed_workout_data_source, changed_calories_expended_data_source, raw_workouts, raw_calories_expended


def patch_raw_birthdate(raw_birthdate, birthdate):
    now_in_nanos = int(datetime.now().timestamp() * 1000000000)
    raw_birthdate['maxEndTimeNs'] = str(now_in_nanos)
    raw_birthdate['point'] = [
        {
            "startTimeNanos": str(now_in_nanos),
            "endTimeNanos": str(now_in_nanos),
            "dataTypeName": "net.pinae.fit.birthdate",
            "originDataSourceId": raw_birthdate['dataSourceId'],
            "value": [
                {
                    "intVal": str(birthdate.timestamp())
                }
            ]
        }
    ]
    return raw_birthdate


def save_token(token):
    with open("saved_token.json", 'w') as f:
        json.dump(token, f)


def load_token():
    if os.path.exists("saved_token.json"):
        with open("saved_token.json", 'r') as f:
            return json.load(f)
    else:
        return None


def delete_token_file():
    if os.path.exists("saved_token.json"):
        os.remove("saved_token.json")
