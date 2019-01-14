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
from datetime import datetime, timedelta
from network_threads import LoadDataSources, LoadWorkouts, LoadCaloriesExpended, LoadWeights, LoadBirthday
from network_threads import LoadNutrition, LoadSex, LoadHeight
from network_threads import CreateDataSource, WriteWorkout, WriteCaloriesExpended, WriteBirthday, WriteSex
from browser_widget import Browser
from layout_helpers import clear_layout
from tests.test_data import guesser_data
from google_fit_api_helpers import extract_workout_data, extract_nutrient_data
from google_fit_api_helpers import merge_calories_expended_with_workouts
from google_fit_api_helpers import patch_raw_workouts_with_changed_activity, patch_raw_birthdate, patch_raw_sex
from google_fit_api_helpers import save_token, load_token, delete_token_file
from tests.print_helpers import print_weights, print_data_sources, print_workouts, print_birthday_data
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
        self.raw_birthday = None
        self.load_birthday_thread = None
        self.load_sex_thread = None
        self.raw_sex_data = None
        self.load_nutrients_thread = None
        self.raw_nutrients = None
        guesser = CalorieGuesser(*guesser_data)
        self.activity_pane = ActivityPane(self.translator, guesser)
        self.activity_pane.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.activity_pane.save_activity_needed.connect(self.save_changed_activity)
        self.activity_pane_scroll_area = QScrollArea()
        self.activity_pane_scroll_area.setWidgetResizable(True)
        self.activity_pane_scroll_area.setContentsMargins(0, 0, 0, 0)
        self.activity_pane_scroll_area.setWidget(self.activity_pane)
        self.nutrients_weight_pane = NutrientsWeightPane(self.translator)
        self.nutrients_weight_pane.save_birthday.connect(self.save_birthday)
        self.nutrients_weight_pane.save_sex.connect(self.save_sex)
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
        token = load_token()
        if token is None:
            self.google_fit = OAuth2Session(
                client_data['installed']['client_id'], scope=scopes,
                redirect_uri=client_data['installed']['redirect_uris'][0])
            authorization_url, state = self.google_fit.authorization_url(
                client_data['installed']['auth_uri'], access_type="offline", prompt="select_account")
            self.loginBrowser.load(authorization_url)
            self.setWindowTitle('Loading')
        else:
            self.google_fit = OAuth2Session(
                client_data['installed']['client_id'], scope=scopes,
                redirect_uri=client_data['installed']['redirect_uris'][0],
                token=token,
                auto_refresh_kwargs={
                    'client_id': client_data['installed']['client_id'],
                    'client_secret': client_data['installed']['client_secret']},
                auto_refresh_url=client_data['installed']['token_uri'],
                token_updater=save_token)
            self.load_all_data()
            self.layout_window()

    def change_title(self, new_title):
        self.setWindowTitle(new_title)

    def process_token(self, approval_code):
        with open("client_id.json") as f:
            client_data = json.load(f)
        self.google_fit.fetch_token(
            client_data['installed']['token_uri'],
            client_secret=client_data['installed']['client_secret'],
            code=approval_code)
        print("--- Oauth finished ---")
        save_token(self.google_fit.token)
        self.load_all_data()
        self.layout_window()

    def load_data_sources(self):
        self.load_data_sources_thread = LoadDataSources(self.google_fit)
        self.load_data_sources_thread.data_loaded.connect(
            self.load_data_sources_callback,
            type=Qt.QueuedConnection)
        self.load_data_sources_thread.start()

    def load_data_sources_callback(self, data_sources):
        if len(data_sources) == 1 and data_sources[0] == "ValueError":
            delete_token_file()
            self.data_sources = []
            self.layout_window()
        else:
            self.data_sources = data_sources
            # print_data_sources(self.data_sources)
            self.load_all_data()

    def load_all_data(self):
        if len(self.data_sources) <= 0:
            self.load_data_sources()
        else:
            self.check_for_custom_data_sources()
            self.load_birthday()
            self.load_sex()
            time_window = timedelta(days=7)
            self.load_workouts(time_window)
            self.load_calories_expended(time_window)
            self.load_weight()
            self.load_nutrients(time_window)

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
        self.nutrients_weight_pane.set_weight_data(self.weights)

    def load_birthday(self):
        self.load_birthday_thread = LoadBirthday(self.google_fit, self.data_sources)
        self.load_birthday_thread.data_loaded.connect(
            self.load_birthday_callback,
            type=Qt.QueuedConnection)
        self.load_birthday_thread.start()

    def load_birthday_callback(self, result_list):
        self.raw_birthday = result_list[0]
        # print_birthday_data(self.raw_birthday)
        if len(self.raw_birthday['point']) > 0:
            self.nutrients_weight_pane.set_birthday(
                datetime.fromtimestamp(self.raw_birthday['point'][-1]['value'][0]['intVal']))

    def load_sex(self):
        self.load_sex_thread = LoadSex(self.google_fit, self.data_sources)
        self.load_sex_thread.data_loaded.connect(
            self.load_sex_callback,
            type=Qt.QueuedConnection)
        self.load_sex_thread.start()

    def load_sex_callback(self, result_list):
        self.raw_sex_data = result_list[0]
        if len(self.raw_sex_data['point']) > 0:
            self.nutrients_weight_pane.set_sex(self.raw_sex_data['point'][-1]['value'][0]['intVal'])

    def load_nutrients(self, time_window):
        self.load_nutrients_thread = LoadNutrition(self.google_fit, self.data_sources, time_window=time_window)
        self.load_nutrients_thread.data_loaded.connect(
            self.load_nutrients_callback,
            type=Qt.QueuedConnection)
        self.load_nutrients_thread.start()

    def load_nutrients_callback(self, raw_nutrients):
        self.raw_nutrients = raw_nutrients
        self.nutrients_weight_pane.set_nutrient_data(extract_nutrient_data(self.raw_nutrients))

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

    def check_for_custom_data_sources(self):
        custom_data_sources = {
            "net.pinae.fit.birthdate": {"created": False, "type": "integer"},
            "net.pinae.fit.sex": {"created": False, "type": "integer"}
        }
        for source in self.data_sources:
            for data_source_name in custom_data_sources.keys():
                if source['dataType']['name'] == data_source_name:
                    custom_data_sources[data_source_name]["created"] = True
        for data_source_name in custom_data_sources.keys():
            if not custom_data_sources[data_source_name]["created"]:
                create_data_source_thread = CreateDataSource(
                    self.google_fit, data_source_name, data_source_type=custom_data_sources[data_source_name]["type"])
                create_data_source_thread.data_loaded.connect(
                    self.data_source_created_callback,
                    type=Qt.QueuedConnection)
                create_data_source_thread.start()
                self.data_sources = []

    def data_source_created_callback(self, response):
        print(response)
        self.check_for_custom_data_sources()

    def save_birthday(self, birthday):
        now_in_nanos = int(datetime.now().timestamp() * 1000000000)
        birthdate_source_id = None
        for source in reversed(self.data_sources):
            if source['dataType']['name'] == "net.pinae.fit.birthdate":
                birthdate_source_id = source['dataStreamId']
        if birthdate_source_id is None:
            print("ERROR: There should be a data source but it is missing!")
            return
        if self.raw_birthday is None:
            birthday_data_source = {
                "minStartTimeNs": str(now_in_nanos),
                "maxEndTimeNs": str(now_in_nanos),
                "dataSourceId": birthdate_source_id,
                "point": [
                    {
                        "startTimeNanos": str(now_in_nanos),
                        "endTimeNanos": str(now_in_nanos),
                        "dataTypeName": "net.pinae.fit.birthdate",
                        "originDataSourceId": birthdate_source_id,
                        "value": [
                            {
                                "intVal": str(birthday.timestamp())
                            }
                        ]
                    }
                ]
            }
        else:
            birthday_data_source = patch_raw_birthdate(self.raw_birthday, birthday)
        save_birthday_thread = WriteBirthday(self.google_fit, birthday_data_source)
        save_birthday_thread.data_loaded.connect(
            self.save_birthday_callback,
            type=Qt.QueuedConnection)
        save_birthday_thread.start()

    def save_birthday_callback(self, result_list):
        self.raw_birthday = result_list[0]
        # print_birthday_data(self.raw_birthday)
        self.nutrients_weight_pane.set_birthday(
            datetime.fromtimestamp(self.raw_birthday['point'][-1]['value'][0]['intVal']))

    def save_sex(self, sex):
        now_in_nanos = int(datetime.now().timestamp() * 1000000000)
        sex_source_id = None
        for source in reversed(self.data_sources):
            if source['dataType']['name'] == "net.pinae.fit.sex":
                sex_source_id = source['dataStreamId']
        if sex_source_id is None:
            print("ERROR: There should be a data source but it is missing!")
            return
        if self.raw_sex_data is None:
            sex_data_source = {
                "minStartTimeNs": str(now_in_nanos),
                "maxEndTimeNs": str(now_in_nanos),
                "dataSourceId": sex_source_id,
                "point": [
                    {
                        "startTimeNanos": str(now_in_nanos),
                        "endTimeNanos": str(now_in_nanos),
                        "dataTypeName": "net.pinae.fit.sex",
                        "originDataSourceId": sex_source_id,
                        "value": [
                            {
                                "intVal": str(sex)
                            }
                        ]
                    }
                ]
            }
        else:
            sex_data_source = patch_raw_sex(self.raw_sex_data, sex)
        save_sex_thread = WriteSex(self.google_fit, sex_data_source)
        save_sex_thread.data_loaded.connect(
            self.save_sex_callback,
            type=Qt.QueuedConnection)
        save_sex_thread.start()

    def save_sex_callback(self, result_list):
        self.raw_sex_data = result_list[0]
        self.nutrients_weight_pane.set_sex(self.raw_sex_data['point'][-1]['value'][0]['intVal'])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    app.exec_()
