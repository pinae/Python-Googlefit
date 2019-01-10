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
        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
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
        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QHBoxLayout()
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(0, 0, 0, 0)
        name_label = QLabel()
        name_label.setText(nutrient['name'])
        self.layout.addWidget(name_label)
        self.layout.addStretch()
        kcal_label = QLabel()
        kcal_label.setText("{:1.0f} kcal".format(nutrient['calories']) if 'calories' in nutrient else
                           translator.incomplete_data)
        kcal_label.setStyleSheet("font-size: 8pt; color: #505050;")
        self.layout.addWidget(kcal_label)
        self.setLayout(self.layout)
        # print(nutrient)
