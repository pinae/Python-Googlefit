#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt
from translator import Translator
from activity_pane import ActivityPane
from nutrients_weight_pane import NutrientsWeightPane
from pane_switcher import PaneSwitcher
from calorie_guesser import CalorieGuesser
from requests_oauthlib import OAuth2Session
from datetime import timedelta
from network_threads import LoadDataSources, LoadWorkouts, LoadCaloriesExpended, LoadWeights
from network_threads import WriteWorkout, WriteCaloriesExpended
from browser_widget import Browser
from layout_helpers import clear_layout
from tests.test_data import guesser_data
from google_fit_api_helpers import extract_workout_data, merge_calories_expended_with_workouts
from google_fit_api_helpers import patch_raw_workouts_with_changed_activity
from tests.print_helpers import print_weights, print_data_sources, print_workouts
from activity_tools import clean_activities
import json
import sys


class MainWindow(QWidget):
    def __init__(self):
        super().__init__(
            flags=Qt.WindowTitleHint | Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setGeometry(0, 0, 800, 1000)
        self.translator = Translator('de')
        self.setWindowTitle(self.translator['window_title'])
        self.google_fit = None
        self.data_sources = []
        self.load_data_sources_thread = None
        self.raw_workouts = []
        self.raw_calories_expended = []
        self.workouts = []
        self.load_workouts_thread = None
        self.load_calories_expended_thread = None
        self.weights = []
        self.load_weights_thread = None
        guesser = CalorieGuesser(*guesser_data)
        self.activity_pane = ActivityPane(self.translator, guesser)
        self.activity_pane.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.activity_pane.save_activity_needed.connect(self.save_changed_activity)
        self.activity_pane_scroll_area = QScrollArea()
        self.activity_pane_scroll_area.setWidgetResizable(True)
        self.activity_pane_scroll_area.setContentsMargins(0, 0, 0, 0)
        self.activity_pane_scroll_area.setWidget(self.activity_pane)
        self.nutrients_weight_pane = NutrientsWeightPane(self.translator)
        self.nutrients_weight_pane_scroll_area = QScrollArea()
        self.nutrients_weight_pane_scroll_area.setWidgetResizable(True)
        self.nutrients_weight_pane_scroll_area.setContentsMargins(0, 0, 0, 0)
        self.nutrients_weight_pane_scroll_area.setWidget(self.nutrients_weight_pane)
        self.panes = [self.activity_pane_scroll_area, self.nutrients_weight_pane_scroll_area]
        self.pane_switcher = PaneSwitcher(self.translator)
        self.pane_switcher.pane_no_selected.connect(self.layout_window)
        self.loginBrowser = None
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout_window()
        self.setLayout(self.layout)
        self.show()

    def layout_window(self, active_pane_no=None):
        clear_layout(self.layout, [self.pane_switcher] + self.panes)
        if type(self.google_fit) is OAuth2Session:
            self.loginBrowser = None
            self.layout.addWidget(self.pane_switcher)
            self.pane_switcher.setVisible(True)
            if active_pane_no is None:
                active_pane_no = self.pane_switcher.get_active_pane_no()
            pane = self.panes[active_pane_no]
            pane.setVisible(True)
            self.layout.addWidget(pane)
        else:
            self.loginBrowser = Browser()
            self.loginBrowser.titleChanged.connect(self.change_title)
            self.loginBrowser.approvalCode_received.connect(self.process_token)
            self.layout.addWidget(self.loginBrowser)
            self.start_google_login()

    def start_google_login(self):
        with open("client_id.json") as f:
            client_data = json.load(f)
        with open("google_fit_api_scopes.json") as f:
            scopes = json.load(f)
        self.google_fit = OAuth2Session(
            client_data['installed']['client_id'], scope=scopes,
            redirect_uri=client_data['installed']['redirect_uris'][0])
        authorization_url, state = self.google_fit.authorization_url(
            client_data['installed']['auth_uri'], access_type="offline", prompt="select_account")
        self.loginBrowser.load(authorization_url)
        self.setWindowTitle('Loading')

    def change_title(self, new_title):
        self.setWindowTitle(new_title)

    def process_token(self, token):
        with open("client_id.json") as f:
            client_data = json.load(f)
        self.google_fit.fetch_token(
            client_data['installed']['token_uri'],
            client_secret=client_data['installed']['client_secret'],
            code=token)
        print(token)
        print("--- Oauth finished ---")
        self.load_all_data()
        self.layout_window()

    def load_data_sources(self):
        self.load_data_sources_thread = LoadDataSources(self.google_fit)
        self.load_data_sources_thread.data_loaded.connect(
            self.load_data_sources_callback,
            type=Qt.QueuedConnection)
        self.load_data_sources_thread.start()

    def load_data_sources_callback(self, data_sources):
        self.data_sources = data_sources
        self.load_all_data()
        # print_data_sources(self.data_sources)

    def load_all_data(self):
        if not self.data_sources:
            self.load_data_sources()
        else:
            time_window = timedelta(days=2)
            self.load_workouts(time_window)
            self.load_calories_expended(time_window)
            self.load_weight()

    def load_workouts(self, time_window):
        self.load_workouts_thread = LoadWorkouts(self.google_fit, self.data_sources,
                                                 time_window=time_window)
        self.load_workouts_thread.data_loaded.connect(
            self.load_workouts_callback,
            type=Qt.QueuedConnection)
        self.load_workouts_thread.start()

    def load_workouts_callback(self, raw_workouts):
        self.raw_workouts = raw_workouts
        workouts = extract_workout_data(self.raw_workouts)
        self.workouts = clean_activities(workouts)
        self.workouts = merge_calories_expended_with_workouts(self.raw_calories_expended, self.workouts)
        self.activity_pane.set_activities(self.workouts)
        # print_workouts(self.workouts)

    def load_calories_expended(self, time_window):
        self.load_calories_expended_thread = LoadCaloriesExpended(self.google_fit, self.data_sources,
                                                                  time_window=time_window)
        self.load_calories_expended_thread.data_loaded.connect(
            self.load_calories_expended_callback,
            type=Qt.QueuedConnection)
        self.load_calories_expended_thread.start()

    def load_calories_expended_callback(self, raw_calories_expended):
        self.raw_calories_expended = raw_calories_expended
        self.workouts = merge_calories_expended_with_workouts(self.raw_calories_expended, self.workouts)
        self.activity_pane.set_activities(self.workouts)

    def load_weight(self):
        self.load_weights_thread = LoadWeights(self.google_fit, self.data_sources,
                                               time_window=timedelta(days=365))
        self.load_weights_thread.data_loaded.connect(
            self.load_weight_callback,
            type=Qt.QueuedConnection)
        self.load_weights_thread.start()

    def load_weight_callback(self, weights):
        self.weights = weights
        # print_weights(self.weights)

    def save_changed_activity(self, activity):
        patch_res = patch_raw_workouts_with_changed_activity(self.raw_workouts, self.raw_calories_expended, activity)
        changed_workout_data_source = patch_res[0]
        changed_calories_expended_data_source = patch_res[1]
        self.raw_workouts = patch_res[2]
        self.raw_calories_expended = patch_res[3]
        if changed_workout_data_source is not None:
            write_workout_thread = WriteWorkout(self.google_fit, changed_workout_data_source)
            write_workout_thread.data_loaded.connect(
                self.write_workout_callback,
                type=Qt.QueuedConnection)
            write_workout_thread.start()
        if changed_calories_expended_data_source is not None:
            write_calories_expended_thread = WriteCaloriesExpended(self.google_fit,
                                                                   changed_calories_expended_data_source)
            write_calories_expended_thread.data_loaded.connect(
                self.write_calories_expended_callback,
                type=Qt.QueuedConnection)
            write_calories_expended_thread.start()

    def write_workout_callback(self, workout_data_source):
        print(workout_data_source[0])

    def write_calories_expended_callback(self, calories_expended_data_source):
        print(calories_expended_data_source[0])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    app.exec_()
