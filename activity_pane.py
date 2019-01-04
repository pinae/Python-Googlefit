#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QWidgetItem, QLabel
from activity_widgets import ActivityDay
from activity_tools import activities_to_days
from layout_helpers import clear_layout


class ActivityPane(QWidget):
    save_activity_needed = pyqtSignal(dict)

    def __init__(self, translator, guesser, *args):
        super(ActivityPane, self).__init__(*args)
        self.guesser = guesser
        self.translator = translator
        self.days = []
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout_pane()

    def layout_pane(self):
        clear_layout(self.layout)
        if len(self.days) == 0:
            empty_notice = QLabel()
            empty_notice.setText(self.translator['no_activities_to_show'])
            self.layout.addWidget(empty_notice)
        for day in self.days:
            day_widget = ActivityDay(day, self.guesser, self.translator)
            day_widget.save_activity_needed.connect(self.relay_save_activity_needed)
            day_widget.setVisible(True)
            self.layout.addWidget(day_widget)
        self.layout.addStretch()
        self.update()

    def set_activities(self, activities):
        self.days = activities_to_days(activities)
        self.layout_pane()

    def relay_save_activity_needed(self, activity):
        self.save_activity_needed.emit(activity)
