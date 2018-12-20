#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from activity_widgets import ActivityDay
from test_data import activity_data


class ActivityPane(QWidget):
    def __init__(self, translator, guesser):
        super(ActivityPane, self).__init__()
        self.translator = translator
        self.layout = QVBoxLayout()
        self.monday_widget = ActivityDay(activity_data, guesser, translator)
        self.layout.addWidget(self.monday_widget)
        self.tuesday_widget = ActivityDay(activity_data, guesser, translator)
        self.layout.addWidget(self.tuesday_widget)
        self.wednesday_widget = ActivityDay(activity_data, guesser, translator)
        self.layout.addWidget(self.wednesday_widget)
        self.tuesday_widget = ActivityDay(activity_data, guesser, translator)
        self.layout.addWidget(self.tuesday_widget)
        self.friday_widget = ActivityDay(activity_data, guesser, translator)
        self.layout.addWidget(self.friday_widget)
        self.saturday_widget = ActivityDay(activity_data, guesser, translator)
        self.layout.addWidget(self.saturday_widget)
        self.sunday_widget = ActivityDay(activity_data, guesser, translator)
        self.layout.addWidget(self.sunday_widget)
        self.layout.addStretch()
        self.setLayout(self.layout)
