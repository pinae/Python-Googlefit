#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtWidgets import QDateTimeEdit, QComboBox
from timed_diagram import TimedActivityBlockDiagram
from google_fit_activity_types import activity_number_map
import abc


class ActivityDay(QWidget):
    def __init__(self, activities, guesser, translator, *args):
        super(ActivityDay, self).__init__(*args)
        self.activities = activities
        self.guesser = guesser
        self.translator = translator
        main_layout = QVBoxLayout()
        diagram_layout = QHBoxLayout()
        self.edit = None
        self.expanded = False
        self.expand_button = QPushButton()
        self.expand_button.setText("Expand")
        self.expand_button.clicked.connect(self.toggle_expanded)
        diagram_layout.addWidget(self.expand_button)
        self.activity_diagram = TimedActivityBlockDiagram(self.guesser)
        self.activity_diagram.set_data(self.activities)
        diagram_layout.addWidget(self.activity_diagram, stretch=1)
        main_layout.addLayout(diagram_layout)
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(0)
        main_layout.addLayout(self.list_layout)
        self.setLayout(main_layout)
        self.update_activity_list()

    def update_activity_list(self):
        for i in reversed(range(self.list_layout.count())):
            self.list_layout.itemAt(i).widget().setParent(None)
        if self.expanded:
            for i, activity in enumerate(self.activities):
                if i == self.edit:
                    item_widget = EditActivity(activity, i, self.translator)
                else:
                    item_widget = DisplayActivity(activity, i, self.translator)
                    item_widget.activity_clicked.connect(self.activity_clicked)
                self.list_layout.addWidget(item_widget)
        self.update()

    def toggle_expanded(self):
        self.expanded = not self.expanded
        self.expand_button.setText("Collapse" if self.expanded else "Expand")
        if not self.expanded:
            self.edit = None
        self.update_activity_list()

    def activity_clicked(self, activity, number):
        self.edit = number
        self.update_activity_list()


class AbstractActivityWidget(QWidget):
    def __init__(self, activity, number, translator, *args):
        super(AbstractActivityWidget, self).__init__(*args)
        self.activity = activity
        self.number = number
        self.translator = translator
        self.even_color = "#f0f0f0"
        self.odd_color = "#c0c0c0"
        self.layout = QVBoxLayout()
        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout_widget(self.layout)
        self.setLayout(self.layout)
        self.set_activity(activity)
        self.set_background_color()

    @abc.abstractmethod
    def layout_widget(self, layout):
        pass

    @abc.abstractmethod
    def set_activity(self, activity):
        self.activity = activity

    def set_background_color(self):
        self.setStyleSheet("background-color: {};".format(self.even_color if self.number % 2 == 0 else self.odd_color))


class EditActivity(AbstractActivityWidget):
    def __init__(self, activity, number, translator, *args):
        self.name_label = QLabel()
        self.name_edit = QComboBox()
        self.start_time_label = QLabel()
        self.start_time_edit = QDateTimeEdit()
        self.end_time_label = QLabel()
        self.end_time_edit = QDateTimeEdit()
        self.margins = 0, 0, 0, 0
        self.label_edit_spacing = 4
        super(EditActivity, self).__init__(activity, number, translator, *args)

    def layout_widget(self, layout):
        self.name_label.setText(self.translator.activity_name_label)
        for name in activity_number_map.keys():
            self.name_edit.addItem(name)
            if activity_number_map[name] == self.activity['activity_no']:
                self.name_edit.setCurrentText(name)
        name_wrapper = QWidget()
        name_wrapper.setContentsMargins(*self.margins)
        name_layout = QHBoxLayout()
        name_layout.setSpacing(self.label_edit_spacing)
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_edit)
        name_layout.addStretch()
        name_wrapper.setLayout(name_layout)
        layout.addWidget(name_wrapper)
        time_wrapper = QWidget()
        time_wrapper.setContentsMargins(*self.margins)
        time_layout = QHBoxLayout()
        time_layout.setSpacing(self.label_edit_spacing)
        self.start_time_label.setText(self.translator.activity_start_time_label)
        self.start_time_edit.setDateTime(self.activity['start_time'])
        time_layout.addWidget(self.start_time_label)
        time_layout.addWidget(self.start_time_edit)
        time_layout.addStretch(1)
        self.end_time_label.setText(self.translator.activity_end_time_label)
        self.end_time_edit.setDateTime(self.activity['end_time'])
        time_layout.addWidget(self.end_time_label)
        time_layout.addWidget(self.end_time_edit)
        time_wrapper.setLayout(time_layout)
        layout.addWidget(time_wrapper)

    def set_activity(self, activity):
        super(EditActivity, self).set_activity(activity)


class DisplayActivity(AbstractActivityWidget):
    activity_clicked = pyqtSignal(dict, int)

    def __init__(self, activity, number, translator, *args):
        self.activity_name = QLabel()
        self.time = QLabel()
        self.calories = QLabel()
        self.name_margins = 4, 4, 4, 0
        self.time_display_style_sheet = "font-size: 8pt; color: #505050;"
        self.time_display_margins = 4, 0, 4, 4
        super(DisplayActivity, self).__init__(activity, number, translator, *args)

    def layout_widget(self, layout):
        self.activity_name.setContentsMargins(*self.name_margins)
        layout.addWidget(self.activity_name)
        date_layout = QHBoxLayout()
        date_layout.setSpacing(0)
        date_layout.setContentsMargins(0, 0, 0, 0)
        self.time.setStyleSheet(self.time_display_style_sheet)
        self.time.setContentsMargins(*self.time_display_margins)
        date_layout.addWidget(self.time, stretch=1)
        self.calories.setStyleSheet(self.time_display_style_sheet)
        self.calories.setContentsMargins(*self.time_display_margins)
        date_layout.addWidget(self.calories)
        layout.addLayout(date_layout)

    def set_activity(self, activity):
        super(DisplayActivity, self).set_activity(activity)
        self.activity_name.setText(activity['activity'])
        duration = activity['end_time'] - activity['start_time']
        self.time.setText(activity['start_time'].strftime("%A, %d.%m.%Y %H:%M") + " - " +
                          activity['end_time'].strftime("%H:%M") + " (" + str(duration) + ")")
        self.calories.setText("1000 kcal")

    def mousePressEvent(self, event):
        self.activity_clicked.emit(self.activity, self.number)
