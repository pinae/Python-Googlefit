#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from requests_oauthlib import OAuth2Session
from urllib.parse import parse_qs
from datetime import timedelta
from network_threads import LoadDataSources, LoadWorkouts, LoadWeights
import time
import json
import sys


class MainWindow(QWidget):
    def __init__(self):
        super().__init__(
            flags=Qt.WindowTitleHint | Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setGeometry(0, 0, 800, 1000)
        self.setWindowTitle('fit.py')
        self.google_fit = None
        self.data_sources = []
        self.load_data_sources_thread = None
        self.workouts = []
        self.load_workouts_thread = None
        self.weights = []
        self.load_weights_thread = None
        self.loginBrowser = None
        self.header_label = QLabel()
        self.header_label.setText("Google Fit")
        self.layout = QHBoxLayout()
        self.layout_window()
        self.setLayout(self.layout)
        self.show()

    def clear_layout(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    def layout_window(self):
        self.clear_layout()
        if type(self.google_fit) is OAuth2Session:
            self.loginBrowser = None
            self.layout.addWidget(self.header_label)
            self.load_all_data()
        else:
            self.loginBrowser = Browser()
            self.loginBrowser.titleChanged.connect(self.change_title)
            self.loginBrowser.approvalCode_recieved.connect(self.process_token)
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


class Browser(QWebEngineView):
    approvalCode_recieved = pyqtSignal(str)
    titleChanged = pyqtSignal(str)

    def __init__(self):
        self.view = QWebEngineView.__init__(self)
        self.setGeometry(0, 0, 800, 1000)
        self.titleChanged.connect(self.adjust_title)
        self.loadFinished.connect(self.page_loaded)

    def load(self, url):
        self.setUrl(QUrl(url))

    def adjust_title(self):
        self.titleChanged.emit(self.title())

    def page_loaded(self):
        url = self.url().toString()
        if url.startswith("https://accounts.google.com/o/oauth2/approval/v2"):
            self.approvalCode_recieved.emit(parse_qs(url)['approvalCode'][0])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    app.exec_()
