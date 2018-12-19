#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from timed_diagram import TimedActivityBlockDiagram
from test_data import activity_data


class ActivityPane(QWidget):
    def __init__(self, translator, guesser):
        super(ActivityPane, self).__init__()
        self.translator = translator
        self.layout = QVBoxLayout()
        self.activity_diagram = TimedActivityBlockDiagram(guesser)
        self.activity_diagram.set_data(activity_data)
        self.layout.addWidget(self.activity_diagram)
        self.setLayout(self.layout)
