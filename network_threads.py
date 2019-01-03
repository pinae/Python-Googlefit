#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals, absolute_import
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime, timedelta
from google_fit_activity_types import activity_map


class LoadThread(Thread, QObject):
    data_loaded = pyqtSignal(list)

    def __init__(self, google_fit, *args):
        super(LoadThread, self).__init__()
        QObject.__init__(self, *args)
        self.google_fit = google_fit


class LoadDataSources(LoadThread):
    def run(self):
        response = self.google_fit.get("https://www.googleapis.com/fitness/v1/users/me/dataSources")
        self.data_loaded.emit(response.json()['dataSource'])
        super(LoadDataSources, self).run()


class LoadWorkouts(LoadThread):
    def __init__(self, google_fit, data_sources, *args, time_window=timedelta(days=7)):
        super(LoadWorkouts, self).__init__(google_fit, *args)
        self.data_sources = data_sources
        self.time_window = time_window

    def run(self):
        workouts = []
        for source in self.data_sources:
            if source['dataType']['name'] == "com.google.activity.segment":
                response = self.google_fit.get(
                    "https://www.googleapis.com/fitness/v1/users/me/dataSources/" +
                    source['dataStreamId'] + "/datasets/" +
                    str(int((datetime.now() - self.time_window).timestamp() * 1000000000)) + "-" +
                    str(int(datetime.now().timestamp() * 1000000000)))
                for activity in response.json()['point']:
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
            if source['dataType']['name'] == "com.google.calories.expended":
                response = self.google_fit.get(
                    "https://www.googleapis.com/fitness/v1/users/me/dataSources/" +
                    source['dataStreamId'] + "/datasets/" +
                    str(int((datetime.now() - self.time_window).timestamp() * 1000000000)) + "-" +
                    str(int(datetime.now().timestamp() * 1000000000)))
                # print(response.json()['dataSourceId'])
                for point in response.json()['point']:
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
        self.data_loaded.emit(workouts)
        super(LoadWorkouts, self).run()


class LoadWeights(LoadThread):
    def __init__(self, google_fit, data_sources, *args, time_window=timedelta(days=365)):
        super(LoadWeights, self).__init__(google_fit, *args)
        self.data_sources = data_sources
        self.time_window = time_window

    def run(self):
        weights = []
        for source in self.data_sources:
            if source['dataType']['name'] == "com.google.weight":
                response = self.google_fit.get(
                    "https://www.googleapis.com/fitness/v1/users/me/dataSources/" +
                    source['dataStreamId'] + "/datasets/" +
                    str(int((datetime.now() - self.time_window).timestamp() * 1000000000)) + "-" +
                    str(int(datetime.now().timestamp() * 1000000000)))
                for activity in response.json()['point']:
                    weights.append({
                        "time": datetime.fromtimestamp(int(activity['startTimeNanos']) / 1000000000),
                        "weight": activity['value'][0]['fpVal']
                    })
        self.data_loaded.emit(weights)
        super(LoadWeights, self).run()
