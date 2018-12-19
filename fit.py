#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from translator import Translator
from activity_pane import ActivityPane
from nutrients_weight_pane import NutrientsWeightPane
from pane_switcher import PaneSwitcher
from calorie_guesser import CalorieGuesser
from requests_oauthlib import OAuth2Session
from datetime import timedelta, datetime
from network_threads import LoadDataSources, LoadWorkouts, LoadWeights
from browser_widget import Browser
from test_data import guesser_data
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
        self.workouts = []
        self.load_workouts_thread = None
        self.weights = []
        self.load_weights_thread = None
        guesser = CalorieGuesser(*guesser_data)
        self.activity_pane = ActivityPane(self.translator, guesser)
        self.nutrients_weight_pane = NutrientsWeightPane(self.translator)
        self.panes = [self.activity_pane, self.nutrients_weight_pane]
        self.pane_switcher = PaneSwitcher(self.translator)
        self.pane_switcher.pane_no_selected.connect(self.layout_window)
        self.loginBrowser = None
        self.header_label = QLabel()
        self.header_label.setText("Google Fit")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout_window()
        self.setLayout(self.layout)
        self.show()

    def clear_layout(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    def layout_window(self, active_pane_no=None):
        self.clear_layout()
        if type(self.google_fit) is OAuth2Session or True:
            self.loginBrowser = None
            self.layout.addWidget(self.pane_switcher)
            if active_pane_no is None:
                active_pane_no = self.pane_switcher.get_active_pane_no()
            pane = self.panes[active_pane_no]
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
        print("Oauth finished")
        # self.load_all_data()
        self.layout_window()

    def load_data_sources(self):
        self.load_data_sources_thread = LoadDataSources(self.load_data_sources_callback, self.google_fit)
        self.load_data_sources_thread.start()

    def load_data_sources_callback(self, data_sources):
        self.data_sources = data_sources
        self.load_all_data()
        for source in self.data_sources:
            print("Data source: " + source['dataStreamId'])
            print("Type: " + source['dataType']['name'])
            for field in source['dataType']['field']:
                print("  - {}: {} {}".format(
                    field['format'],
                    field['name'],
                    "(optional)" if 'optional' in field and field['optional'] else ""))
            if 'application' in source:
                print("App: " + source['application']['packageName'])
            if 'device' in source:
                print("Gerät: {} - {} (Typ: {} mit uid: {})".format(
                    source['device']['manufacturer'],
                    source['device']['model'],
                    source['device']['type'],
                    source['device']['uid']))
            print("---------------------------------------------")

    def load_all_data(self):
        if not self.data_sources:
            self.load_data_sources()
        else:
            self.load_workouts()
            self.load_weight()

    def load_workouts(self):
        self.load_workouts_thread = LoadWorkouts(self.load_workouts_callback, self.google_fit, self.data_sources,
                                                 time_window=timedelta(days=7))
        self.load_workouts_thread.start()

    def load_workouts_callback(self, workouts):
        self.workouts = workouts
        for workout in self.workouts:
            print("- {} ({} - {})".format(
                workout['activity'],
                str(workout['start_time']),
                str(workout['end_time'])))

    def load_weight(self):
        self.load_weights_thread = LoadWeights(self.load_weight_callback, self.google_fit, self.data_sources,
                                               time_window=timedelta(days=365))
        self.load_weights_thread.start()

    def load_weight_callback(self, weights):
        self.weights = weights
        for weight in self.weights:
            print("Gewicht {}kg am {}.".format(
                weight['weight'],
                str(weight['time'])))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    app.exec_()
