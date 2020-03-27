# -*- coding: utf-8 -*-
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


def extract_nutrient_data(raw_nurient_data):
    meal_items = []
    for raw_data in raw_nurient_data:
        for item in raw_data['point']:
            meal_item = {
                "dataSourceId": raw_data['dataSourceId'],
                "start_time": datetime.fromtimestamp(int(item['startTimeNanos']) / 1000000000),
                "end_time": datetime.fromtimestamp(int(item['endTimeNanos']) / 1000000000)
            }
            if len(item['value']) >= 2 and 'intVal' in item['value'][1]:
                meal_item["meal_type"] = item['value'][1]['intVal']
            if len(item['value']) >= 3 and 'stringVal' in item['value'][2]:
                meal_item["name"] = item['value'][2]['stringVal']
            for map_pair in item['value'][0]['mapVal']:
                if 'fpVal' in map_pair['value']:
                    map_value = map_pair['value']['fpVal']
                elif 'intVal' in map_pair['value']:
                    map_value = map_pair['value']['intVal']
                elif 'stringVal' in map_pair['value']:
                    map_value = map_pair['value']['stringVal']
                else:
                    map_value = "unable to read value"
                meal_item[map_pair['key']] = map_value
            meal_items.append(meal_item)
    return meal_items


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
                    "intVal": str(int(birthdate.timestamp()))
                }
            ]
        }
    ]
    return raw_birthdate


def patch_raw_sex(raw_sex_data, sex):
    now_in_nanos = int(datetime.now().timestamp() * 1000000000)
    raw_sex_data['maxEndTimeNs'] = str(now_in_nanos)
    raw_sex_data['point'] = [
        {
            "startTimeNanos": str(now_in_nanos),
            "endTimeNanos": str(now_in_nanos),
            "dataTypeName": "net.pinae.fit.sex",
            "originDataSourceId": raw_sex_data['dataSourceId'],
            "value": [
                {
                    "intVal": str(sex)
                }
            ]
        }
    ]
    return raw_sex_data


def find_most_recent_height(raw_height_data):
    height_datasets = []
    for height_data_source in raw_height_data:
        for point in height_data_source['point']:
            dataset = {'time': datetime.fromtimestamp(int(point['endTimeNanos']) / 1000000000)}
            if 'modifiedTimeMillis' in point:
                dataset['time'] = datetime.fromtimestamp(int(point['modifiedTimeMillis']) / 1000)
            dataset['height'] = point['value'][0]['fpVal']
            height_datasets.append(dataset)
    return sorted(height_datasets, key=lambda x: x['time'])[-1]['height']


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
