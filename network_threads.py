#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals, absolute_import
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime, timedelta
from google_fit_activity_types import activity_map


class GoogleFitAPIRequestThread(Thread, QObject):
    data_loaded = pyqtSignal(list)

    def __init__(self, google_fit, *args):
        super(GoogleFitAPIRequestThread, self).__init__()
        QObject.__init__(self, *args)
        self.google_fit = google_fit


class LoadDataSources(GoogleFitAPIRequestThread):
    def run(self):
        response = self.google_fit.get("https://www.googleapis.com/fitness/v1/users/me/dataSources")
        self.data_loaded.emit(response.json()['dataSource'])
        super(LoadDataSources, self).run()


class LoadWorkouts(GoogleFitAPIRequestThread):
    def __init__(self, google_fit, data_sources, *args, time_window=timedelta(days=7)):
        super(LoadWorkouts, self).__init__(google_fit, *args)
        self.data_sources = data_sources
        self.time_window = time_window

    def run(self):
        raw_workouts = []
        for source in self.data_sources:
            if source['dataType']['name'] == "com.google.activity.segment":
                response = self.google_fit.get(
                    "https://www.googleapis.com/fitness/v1/users/me/dataSources/" +
                    source['dataStreamId'] + "/datasets/" +
                    str(int((datetime.now() - self.time_window).timestamp() * 1000000000)) + "-" +
                    str(int(datetime.now().timestamp() * 1000000000)))
                raw_workouts.append(response.json())
        self.data_loaded.emit(raw_workouts)
        super(LoadWorkouts, self).run()


class LoadCaloriesExpended(GoogleFitAPIRequestThread):
    def __init__(self, google_fit, data_sources, *args, time_window=timedelta(days=7)):
        super(LoadCaloriesExpended, self).__init__(google_fit, *args)
        self.data_sources = data_sources
        self.time_window = time_window

    def run(self):
        raw_calories_expended = []
        for source in self.data_sources:
            if source['dataType']['name'] == "com.google.calories.expended":
                response = self.google_fit.get(
                    "https://www.googleapis.com/fitness/v1/users/me/dataSources/" +
                    source['dataStreamId'] + "/datasets/" +
                    str(int((datetime.now() - self.time_window).timestamp() * 1000000000)) + "-" +
                    str(int(datetime.now().timestamp() * 1000000000)))
                raw_calories_expended.append(response.json())
        self.data_loaded.emit(raw_calories_expended)
        super(LoadCaloriesExpended, self).run()


class LoadWeights(GoogleFitAPIRequestThread):
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


class WriteWorkout(GoogleFitAPIRequestThread):
    def __init__(self, google_fit, data_source_id, *args):
        super(WriteWorkout, self).__init__(google_fit, *args)
        self.data_source_id = data_source_id

    def run(self):
        response = self.google_fit.patch(
            "https://www.googleapis.com/fitness/v1/users/me/dataSources/" +
            self.data_source_id + "/datasets/" +
            str()

        )
        super(WriteWorkout, self).run()
