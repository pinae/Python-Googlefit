#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel


class NutrientsList(QWidget):
    def __init__(self, translator, *args):
        self.translator = translator
        super(NutrientsList, self).__init__(*args)
        self.nutrients = []
        self.even_color = "#f0f0f0"
        self.odd_color = "#c0c0c0"
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout_list()

    def layout_list(self):
        for i, n in enumerate(self.nutrients):
            nw = NutrientWidget(self.translator, n)
            nw.setStyleSheet("background-color: {};".format(self.even_color if i % 2 == 0 else self.odd_color))
            self.layout.addWidget(nw)

    def set_nutrients(self, nutrients=[]):
        self.nutrients = nutrients
        self.layout_list()


class NutrientWidget(QWidget):
    def __init__(self, translator, nutrient, *args):
        self.translator = translator
        super(NutrientWidget, self).__init__(*args)
        self.layout = QVBoxLayout()
        label = QLabel()
        label.setText("nothing")
        self.layout.addWidget(label)
        self.setLayout(self.layout)
        print(nutrient)
