#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from timed_diagram import TimedLineChart
from tests.test_data import weight_data


class NutrientsWeightPane(QWidget):
    def __init__(self, translator):
        super(NutrientsWeightPane, self).__init__()
        self.translator = translator
        self.layout = QVBoxLayout()
        self.weight_diagram = TimedLineChart()
        self.weight_diagram.set_data(weight_data)
        self.layout.addWidget(self.weight_diagram)
        self.setLayout(self.layout)
