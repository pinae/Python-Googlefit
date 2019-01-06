#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QPushButton
from timed_diagram import TimedLineChart
from datetime import datetime
from tests.test_data import weight_data


class NutrientsWeightPane(QWidget):
    save_birthday = pyqtSignal(datetime)

    def __init__(self, translator):
        super(NutrientsWeightPane, self).__init__()
        self.translator = translator
        self.layout = QVBoxLayout()
        birthday_layout = QHBoxLayout()
        birthday_label = QLabel()
        birthday_label.setText(translator.birthday_label)
        birthday_layout.addWidget(birthday_label)
        self.birthday_day = QSpinBox()
        self.birthday_day.setRange(0, 31)
        self.birthday_day.setValue(15)
        birthday_layout.addWidget(self.birthday_day)
        self.birthday_month = QSpinBox()
        self.birthday_month.setRange(1, 12)
        self.birthday_month.setValue(6)
        birthday_layout.addWidget(self.birthday_month)
        self.birthday_year = QSpinBox()
        self.birthday_year.setRange(1890, 2032)
        self.birthday_year.setValue(1980)
        birthday_layout.addWidget(self.birthday_year)
        birthday_layout.addStretch()
        save_button = QPushButton()
        save_button.setText(translator.save_button)
        save_button.setDisabled(True)
        save_button.clicked.connect(self.save_button_clicked)
        birthday_layout.addWidget(save_button)
        self.layout.addLayout(birthday_layout)
        self.weight_diagram = TimedLineChart()
        self.weight_diagram.set_data([])
        self.layout.addWidget(self.weight_diagram)
        self.setLayout(self.layout)

    def save_button_clicked(self):
        birthday = datetime(year=self.birthday_year.value(),
                            month=self.birthday_month.value(),
                            day=self.birthday_day.value())
        self.save_birthday.emit(birthday)

    def set_birthday(self, birthday):
        self.birthday_year.setValue(birthday.year)
        self.birthday_month.setValue(birthday.month)
        self.birthday_day.setValue(birthday.day)

    def set_weight_data(self, weights):
        self.weight_diagram.set_data(weights)
