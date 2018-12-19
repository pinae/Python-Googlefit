#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from timed_diagram import TimedActivityBlockDiagram
import abc


class ActivityDay(QWidget):
    def __init__(self, activities, guesser, *args):
        super(ActivityDay, self).__init__(*args)
        self.activities = activities
        self.guesser = guesser
        main_layout = QVBoxLayout()
        diagram_layout = QHBoxLayout()
        expand_button = QPushButton()
        expand_button.setText("Toggle")
        diagram_layout.addWidget(expand_button)
        self.activity_diagram = TimedActivityBlockDiagram(self.guesser)
        self.activity_diagram.set_data(self.activities)
        diagram_layout.addWidget(self.activity_diagram, stretch=1)
        main_layout.addLayout(diagram_layout)
        self.list_layout = QVBoxLayout()
        main_layout.addLayout(self.list_layout)
        self.setLayout(main_layout)
        self.update_activity_list()

    def update_activity_list(self):
        for i in reversed(range(self.list_layout.count())):
            self.list_layout.itemAt(i).widget().setParent(None)
        for activity in self.activities:
            display_widget = DisplayActivity(activity)
            self.list_layout.addWidget(display_widget)
        self.update()


class AbstractActivityWidget(QWidget):
    def __init__(self, activity, *args):
        super(AbstractActivityWidget, self).__init__(*args)
        self.activity = activity
        self.layout = QVBoxLayout()
        self.layout_widget(self.layout)
        self.setLayout(self.layout)
        self.set_activity(activity)

    @abc.abstractmethod
    def layout_widget(self, layout):
        pass

    @abc.abstractmethod
    def set_activity(self, activity):
        self.activity = activity


class EditActivity(AbstractActivityWidget):
    def __init__(self, activity, *args):
        super(EditActivity, self).__init__(activity, *args)

    def layout_widget(self, layout):
        pass

    def set_activity(self, activity):
        super(EditActivity, self).set_activity(activity)


class DisplayActivity(AbstractActivityWidget):
    activity_clicked = pyqtSignal(dict)

    def __init__(self, activity, *args):
        self.activity_name = QLabel()
        self.start_time = QLabel()
        self.end_time = QLabel()
        self.time_display_style_sheet = "font-size: 8pt; color: #505050;"
        super(DisplayActivity, self).__init__(activity, *args)

    def layout_widget(self, layout):
        layout.addWidget(self.activity_name)
        date_layout = QHBoxLayout()
        self.start_time.setStyleSheet(self.time_display_style_sheet)
        date_layout.addWidget(self.start_time)
        self.end_time.setStyleSheet(self.time_display_style_sheet)
        date_layout.addWidget(self.end_time)
        layout.addLayout(date_layout)

    def set_activity(self, activity):
        super(DisplayActivity, self).set_activity(activity)
        self.activity_name.setText(activity['activity'])
        self.start_time.setText(activity['start_time'].strftime("%A, %d.%m.%Y %H:%M"))
        self.end_time.setText(activity['end_time'].strftime("%H:%M"))

    def mousePressEvent(self, event):
        self.activity_clicked.emit(self.activity)
