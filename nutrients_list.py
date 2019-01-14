#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from nutrients_helpers import distribute_nutrition_data_to_meals, day_calorie_sum, meal_calorie_sum
from layout_helpers import clear_layout


class NutrientsList(QWidget):
    def __init__(self, translator, *args):
        self.translator = translator
        super(NutrientsList, self).__init__(*args)
        self.nutrient_days = []
        self.even_color = "#f0f0f0"
        self.odd_color = "#c0c0c0"
        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.layout_list()
        self.weekdays = [
            self.translator.monday,
            self.translator.tuesday,
            self.translator.wednesday,
            self.translator.thursday,
            self.translator.friday,
            self.translator.saturday,
            self.translator.sunday
        ]

    def layout_list(self):
        clear_layout(self.layout)
        for day in self.nutrient_days:
            if len(day) < 1:
                continue
            day_heading_wrapper = QWidget()
            day_heading_wrapper.setStyleSheet("background-color: #1e1e1e;")
            day_heading_layout = QHBoxLayout()
            day_heading = QLabel()
            day_heading.setText(self.weekdays[day[0]['items'][0]['end_time'].weekday()])
            day_heading.setStyleSheet("font-size: 18pt; font-weight: bold; color: #ffffff;")
            day_heading_layout.addWidget(day_heading)
            day_date_label = QLabel()
            day_date_label.setText(day[0]['items'][0]['end_time'].strftime(self.translator.date_format))
            day_date_label.setStyleSheet("font-size: 12pt; color: #909090;")
            day_heading_layout.addWidget(day_date_label)
            day_heading_layout.addStretch()
            day_sum_label = QLabel()
            day_sum_label.setText(self.translator.sum + ": {:1.0f} kcal".format(day_calorie_sum(day)))
            day_sum_label.setStyleSheet("font-size: 8pt; color: #909090;")
            day_heading_layout.addWidget(day_sum_label)
            day_heading_wrapper.setLayout(day_heading_layout)
            self.layout.addWidget(day_heading_wrapper)
            for meal in day:
                meal_heading_wrapper = QWidget()
                meal_heading_wrapper.setStyleSheet("background-color: #909090;")
                meal_heading_layout = QHBoxLayout()
                meal_heading = QLabel()
                meal_heading.setText(meal['name'])
                meal_heading.setStyleSheet("font-size: 14pt; font-weight: bold;")
                meal_heading_layout.addWidget(meal_heading)
                meal_heading_layout.addStretch()
                meal_sum_label = QLabel()
                meal_sum_label.setText(self.translator.sum + ": {:1.0f} kcal".format(meal_calorie_sum(meal)))
                meal_sum_label.setStyleSheet("font-size: 8pt; color: #000000;")
                meal_heading_layout.addWidget(meal_sum_label)
                meal_heading_wrapper.setLayout(meal_heading_layout)
                self.layout.addWidget(meal_heading_wrapper)
                for i, item in enumerate(meal['items']):
                    meal_item_wrapper = QWidget()
                    meal_item_wrapper.setStyleSheet("background-color: {};".format(
                        self.even_color if i % 2 > 0 else self.odd_color))
                    meal_item_layout = QHBoxLayout()
                    meal_item = NutrientWidget(self.translator, item)
                    meal_item_layout.addWidget(meal_item)
                    meal_item_wrapper.setLayout(meal_item_layout)
                    self.layout.addWidget(meal_item_wrapper)

    def set_nutrients(self, nutrients=[]):
        self.nutrient_days = distribute_nutrition_data_to_meals(nutrients, self.translator)
        from tests.print_helpers import print_nutrient_meal_days
        # print_nutrient_meal_days(self.nutrient_days)
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
