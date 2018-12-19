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
        self.day_widget = ActivityDay(activity_data, guesser)
        self.layout.addWidget(self.day_widget)
        self.layout.addStretch()
        self.setLayout(self.layout)
