#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QPushButton
from timed_diagram import TimedLineChart
from nutrients_list import NutrientsList
from datetime import datetime


class NutrientsWeightPane(QWidget):
    save_birthday = pyqtSignal(datetime)
    save_sex = pyqtSignal(int)

    def __init__(self, translator):
        super(NutrientsWeightPane, self).__init__()
        self.birthday = None
        self.translator = translator
        self.layout = QVBoxLayout()
        birthday_layout = QHBoxLayout()
        birthday_label = QLabel()
        birthday_label.setText(translator.birthday_label)
        birthday_layout.addWidget(birthday_label)
        self.birthday_day = QSpinBox()
        self.birthday_day.setRange(0, 31)
        self.birthday_day.setValue(15)
        self.birthday_day.valueChanged.connect(self.check_for_birthday_change)
        birthday_layout.addWidget(self.birthday_day)
        self.birthday_month = QSpinBox()
        self.birthday_month.setRange(1, 12)
        self.birthday_month.setValue(6)
        self.birthday_month.valueChanged.connect(self.check_for_birthday_change)
        birthday_layout.addWidget(self.birthday_month)
        self.birthday_year = QSpinBox()
        self.birthday_year.setRange(1890, 2032)
        self.birthday_year.setValue(1980)
        self.birthday_year.valueChanged.connect(self.check_for_birthday_change)
        birthday_layout.addWidget(self.birthday_year)
        birthday_layout.addStretch()
        self.save_button = QPushButton()
        self.save_button.setText(translator.save_button)
        self.save_button.clicked.connect(self.save_button_clicked)
        birthday_layout.addWidget(self.save_button)
        self.layout.addLayout(birthday_layout)
        sex_layout = QHBoxLayout()
        self.female_button = QPushButton()
        self.female_button.setText("♀")
        self.female_button.clicked.connect(self.female_button_clicked)
        self.male_button = QPushButton()
        self.male_button.setText("♂")
        self.male_button.clicked.connect(self.male_button_clicked)
        sex_layout.addWidget(self.female_button)
        sex_layout.addWidget(self.male_button)
        self.layout.addLayout(sex_layout)
        self.weight_diagram = TimedLineChart()
        self.weight_diagram.setMinimumHeight(150)
        self.weight_diagram.set_data([])
        self.layout.addWidget(self.weight_diagram)
        self.nutrients_list = NutrientsList(self.translator)
        self.layout.addWidget(self.nutrients_list)
        self.setLayout(self.layout)
        self.check_for_birthday_change()

    def save_button_clicked(self):
        self.birthday = datetime(year=self.birthday_year.value(),
                                 month=self.birthday_month.value(),
                                 day=self.birthday_day.value())
        self.save_birthday.emit(self.birthday)

    def female_button_clicked(self):
        self.set_sex(0)
        self.save_sex.emit(0)

    def male_button_clicked(self):
        self.set_sex(1)
        self.save_sex.emit(1)

    def check_for_birthday_change(self):
        if self.birthday is None:
            self.save_button.setDisabled(False)
        elif type(self.birthday) is datetime:
            self.save_button.setDisabled(self.birthday.year == self.birthday_year.value() and
                                         self.birthday.month == self.birthday_month.value() and
                                         self.birthday.day == self.birthday_day.value())
        try:
            birthday = datetime(year=self.birthday_year.value(),
                                month=self.birthday_month.value(),
                                day=self.birthday_day.value())
        except ValueError:
            self.save_button.setDisabled(True)

    def set_birthday(self, birthday):
        self.birthday = birthday
        self.birthday_year.setValue(birthday.year)
        self.birthday_month.setValue(birthday.month)
        self.birthday_day.setValue(birthday.day)
        self.check_for_birthday_change()

    def set_weight_data(self, weights):
        weight_list = []
        for w in sorted(weights, key=lambda x: x['time']):
            if len(weight_list) < 1 or w['time'] > weight_list[-1][0]:
                weight_list.append((w['time'], w['weight']))
        self.weight_diagram.set_data(weight_list)

    def set_nutrient_data(self, nutrients):
        self.nutrients_list.set_nutrients(nutrients)

    def set_sex(self, sex):
        self.female_button.setEnabled(sex != 0)
        self.male_button.setEnabled(sex != 1)
        if sex == 0:
            self.female_button.setStyleSheet("background-color: #ef00b7;")
            self.male_button.setStyleSheet("")
        else:
            self.female_button.setStyleSheet("")
            self.male_button.setStyleSheet("background-color: #ef00b7;")
