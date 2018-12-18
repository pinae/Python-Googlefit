#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals, absolute_import
from threading import Thread
from datetime import datetime, timedelta
from google_fit_activity_types import activity_map


class LoadDataSources(Thread):
    def __init__(self, callback, google_fit, *args):
        super(LoadDataSources, self).__init__(*args)
        self.callback = callback
        self.google_fit = google_fit

    def run(self):
        if callable(self.callback):
            response = self.google_fit.get("https://www.googleapis.com/fitness/v1/users/me/dataSources")
            self.callback(response.json()['dataSource'])
        super(LoadDataSources, self).run()


class LoadWorkouts(Thread):
    def __init__(self, callback, google_fit, data_sources, *args, time_window=timedelta(days=7)):
        super(LoadWorkouts, self).__init__(*args)
        self.callback = callback
        self.google_fit = google_fit
        self.data_sources = data_sources
        self.time_window = time_window

    def run(self):
        if callable(self.callback):
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
                            "activity_no": activity_map[activity['value'][0]['intVal']],
                            "start_time": datetime.fromtimestamp(int(activity['startTimeNanos']) / 1000000000),
                            "end_time": datetime.fromtimestamp(int(activity['endTimeNanos']) / 1000000000)
                        }
                        if 'originDataSourceId' in activity:
                            workout["sourceId"] = activity['originDataSourceId']
                        workouts.append(workout)
            self.callback(workouts)
        super(LoadWorkouts, self).run()


class LoadWeights(Thread):
    def __init__(self, callback, google_fit, data_sources, *args, time_window=timedelta(days=365)):
        super(LoadWeights, self).__init__(*args)
        self.callback = callback
        self.google_fit = google_fit
        self.data_sources = data_sources
        self.time_window = time_window

    def run(self):
        if callable(self.callback):
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
            self.callback(weights)
        super(LoadWeights, self).run()
