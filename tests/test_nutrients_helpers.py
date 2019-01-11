#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from nutrients_helpers import distribute_nutrition_data_to_meals, filter_data_with_calories, split_days, extract_snacks
from translator import Translator
from tests.print_helpers import print_nutrient_meal_days
from datetime import datetime
import unittest


class TestDistributeNutritionDataToMeals(unittest.TestCase):
    def test_tree_meals_day(self):
        data = [
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                "name": "Müsli", "calories": 230
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                "name": "Milch", "calories": 97.37
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                "name": "Schnitzel", "calories": 176.3
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                "name": "Pommes", "calories": 237.689
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                "name": "Salat", "calories": 27.4567
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                "name": "Brot", "calories": 167
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                "name": "Wurst", "calories": 81.2
            }
        ]
        expected = [
            [
                {'name': "Frühstück", 'items': [
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                        "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                        "name": "Müsli", "calories": 230
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                        "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                        "name": "Milch", "calories": 97.37
                    }
                ]},
                {'name': "Mittagessen", 'items': [
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                        "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                        "name": "Schnitzel", "calories": 176.3
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                        "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                        "name": "Pommes", "calories": 237.689
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                        "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                        "name": "Salat", "calories": 27.4567
                    }
                ]},
                {'name': "Abendessen", 'items': [
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                        "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                        "name": "Brot", "calories": 167
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                        "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                        "name": "Wurst", "calories": 81.2
                    }
                ]}
            ]
        ]
        translator = Translator('de', base_path='..')
        result = distribute_nutrition_data_to_meals(data, translator)
        self.assertEqual(len(result), len(expected))
        for i, day in enumerate(result):
            for j, meal in enumerate(day):
                self.assertEqual(meal['name'], expected[i][j]['name'])
                for k, item in enumerate(meal['items']):
                    self.assertEqual(item['name'], expected[i][j]['items'][k]['name'])
                    self.assertEqual(item['start_time'], expected[i][j]['items'][k]['start_time'])
                    self.assertEqual(item['end_time'], expected[i][j]['items'][k]['end_time'])
                    for key in expected[i][j]['items'][k].keys():
                        self.assertIn(key, item)
                        self.assertEqual(expected[i][j]['items'][k][key], item[key])

    def test_only_breakfast(self):
        data = [
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                "name": "Müsli", "calories": 230
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                "name": "Milch", "calories": 97.37
            }
        ]
        expected = [
            [
                {'name': "Frühstück", 'items': [
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                        "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                        "name": "Müsli", "calories": 230
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                        "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                        "name": "Milch", "calories": 97.37
                    }
                ]}
            ]
        ]
        translator = Translator('de', base_path='..')
        result = distribute_nutrition_data_to_meals(data, translator)
        self.assertEqual(len(result), len(expected))
        for i, day in enumerate(result):
            self.assertEqual(len(day), len(expected[i]))
            for j, meal in enumerate(day):
                self.assertEqual(meal['name'], expected[i][j]['name'])
                for k, item in enumerate(meal['items']):
                    self.assertEqual(item['name'], expected[i][j]['items'][k]['name'])
                    self.assertEqual(item['start_time'], expected[i][j]['items'][k]['start_time'])
                    self.assertEqual(item['end_time'], expected[i][j]['items'][k]['end_time'])
                    for key in expected[i][j]['items'][k].keys():
                        self.assertIn(key, item)
                        self.assertEqual(expected[i][j]['items'][k][key], item[key])

    def test_only_Lunch(self):
        data = [
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=20, minute=0),
                "end_time": datetime(year=2019, month=1, day=1, hour=20, minute=0),
                "name": "Müsli", "calories": 230
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=20, minute=1),
                "end_time": datetime(year=2019, month=1, day=1, hour=20, minute=1),
                "name": "Milch", "calories": 97.37
            }
        ]
        expected = [
            [
                {'name': "Abendessen", 'items': [
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=20, minute=0),
                        "end_time": datetime(year=2019, month=1, day=1, hour=20, minute=0),
                        "name": "Müsli", "calories": 230
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=20, minute=1),
                        "end_time": datetime(year=2019, month=1, day=1, hour=20, minute=1),
                        "name": "Milch", "calories": 97.37
                    }
                ]}
            ]
        ]
        translator = Translator('de', base_path='..')
        result = distribute_nutrition_data_to_meals(data, translator)
        print_nutrient_meal_days(result)
        self.assertEqual(len(result), len(expected))
        for i, day in enumerate(result):
            self.assertEqual(len(day), len(expected[i]))
            for j, meal in enumerate(day):
                self.assertEqual(meal['name'], expected[i][j]['name'])
                for k, item in enumerate(meal['items']):
                    self.assertEqual(item['name'], expected[i][j]['items'][k]['name'])
                    self.assertEqual(item['start_time'], expected[i][j]['items'][k]['start_time'])
                    self.assertEqual(item['end_time'], expected[i][j]['items'][k]['end_time'])
                    for key in expected[i][j]['items'][k].keys():
                        self.assertIn(key, item)
                        self.assertEqual(expected[i][j]['items'][k][key], item[key])

    def test_no_lunch(self):
        data = [
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                "name": "Müsli", "calories": 230
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                "name": "Milch", "calories": 97.37
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                "name": "Schnitzel", "calories": 176.3
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                "name": "Pommes", "calories": 237.689
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                "name": "Salat", "calories": 27.4567
            }
        ]
        expected = [
            [
                {'name': "Frühstück", 'items': [
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                        "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                        "name": "Müsli", "calories": 230
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                        "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                        "name": "Milch", "calories": 97.37
                    }
                ]},
                {'name': "Mittagessen", 'items': [
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                        "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                        "name": "Schnitzel", "calories": 176.3
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                        "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                        "name": "Pommes", "calories": 237.689
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                        "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                        "name": "Salat", "calories": 27.4567
                    }
                ]}
            ]
        ]
        translator = Translator('de', base_path='..')
        result = distribute_nutrition_data_to_meals(data, translator)
        self.assertEqual(len(result), len(expected))
        for i, day in enumerate(result):
            self.assertEqual(len(day), len(expected[i]))
            for j, meal in enumerate(day):
                self.assertEqual(meal['name'], expected[i][j]['name'])
                for k, item in enumerate(meal['items']):
                    self.assertEqual(item['name'], expected[i][j]['items'][k]['name'])
                    self.assertEqual(item['start_time'], expected[i][j]['items'][k]['start_time'])
                    self.assertEqual(item['end_time'], expected[i][j]['items'][k]['end_time'])
                    for key in expected[i][j]['items'][k].keys():
                        self.assertIn(key, item)
                        self.assertEqual(expected[i][j]['items'][k][key], item[key])

    def test_bunch_day(self):
        data = [
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=0),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=0),
                "name": "Brötchen", "calories": 250
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=1),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=1),
                "name": "Marmelade", "calories": 30
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=2),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=2),
                "name": "Orangensaft", "calories": 50
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                "name": "Räucherlachs", "calories": 116.3
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                "name": "Gouda", "calories": 90
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                "name": "Salat", "calories": 15
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                "name": "Brot", "calories": 167
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                "name": "Wurst", "calories": 81.2
            }
        ]
        expected = [
            [
                {'name': "Brunch", 'items': [
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=0),
                        "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=0),
                        "name": "Brötchen", "calories": 250
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=1),
                        "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=1),
                        "name": "Marmelade", "calories": 30
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=2),
                        "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=2),
                        "name": "Orangensaft", "calories": 50
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                        "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                        "name": "Räucherlachs", "calories": 116.3
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                        "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                        "name": "Gouda", "calories": 90
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                        "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                        "name": "Salat", "calories": 15
                    }
                ]},
                {'name': "Abendessen", 'items': [
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                        "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                        "name": "Brot", "calories": 167
                    },
                    {
                        "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                        "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                        "name": "Wurst", "calories": 81.2
                    }
                ]}
            ]
        ]
        translator = Translator('de', base_path='..')
        result = distribute_nutrition_data_to_meals(data, translator)
        self.assertEqual(len(result), len(expected))
        for i, day in enumerate(result):
            self.assertEqual(len(day), len(expected[i]))
            for j, meal in enumerate(day):
                self.assertEqual(meal['name'], expected[i][j]['name'])
                for k, item in enumerate(meal['items']):
                    self.assertEqual(item['name'], expected[i][j]['items'][k]['name'])
                    self.assertEqual(item['start_time'], expected[i][j]['items'][k]['start_time'])
                    self.assertEqual(item['end_time'], expected[i][j]['items'][k]['end_time'])
                    for key in expected[i][j]['items'][k].keys():
                        self.assertIn(key, item)
                        self.assertEqual(expected[i][j]['items'][k][key], item[key])


class TestFilterDataWithCalories(unittest.TestCase):
    def test_incomplete_list(self):
        data = [
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                "name": "Müsli", "calories": 230.5
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                "name": "Milch", "calories": 93.863
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                "name": "Schnitzel"
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                "name": "Pommes"
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                "name": "Salat"
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                "name": "Brot", "calories": 128.68934
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                "name": "Wurst"
            }
        ]
        expected = [
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                "name": "Müsli", "calories": 230.5
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                "name": "Milch", "calories": 93.863
            },
            {
                "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                "name": "Brot", "calories": 128.68934
            }
        ]
        filtered = filter_data_with_calories(data)
        self.assertEqual(len(filtered), len(expected))
        for j, meal in enumerate(filtered):
            self.assertEqual(meal['name'], expected[j]['name'])
            self.assertEqual(meal['name'], expected[j]['name'])
            self.assertEqual(meal['start_time'], expected[j]['start_time'])
            self.assertEqual(meal['end_time'], expected[j]['end_time'])
            for key in expected[j].keys():
                self.assertIn(key, meal)
                self.assertEqual(expected[j][key], meal[key])


class TestSplitDays(unittest.TestCase):
    def test_list_with_missing_days(self):
        data = [
            {"start_time": datetime(year=2019, month=1, day=1, hour=3, minute=0),
             "end_time": datetime(year=2019, month=1, day=1, hour=3, minute=0)},
            {"end_time": datetime(year=2019, month=1, day=1, hour=8, minute=0)},
            {"end_time": datetime(year=2019, month=1, day=1, hour=12, minute=0)},
            {"end_time": datetime(year=2019, month=1, day=1, hour=22, minute=0)},
            {"end_time": datetime(year=2019, month=1, day=2, hour=3, minute=0)},
            {"end_time": datetime(year=2019, month=1, day=2, hour=8, minute=0)},
            {"end_time": datetime(year=2019, month=1, day=2, hour=14, minute=0)},
            {"end_time": datetime(year=2019, month=1, day=7, hour=8, minute=0)},
            {"end_time": datetime(year=2019, month=1, day=7, hour=13, minute=0)},
            {"end_time": datetime(year=2019, month=1, day=8, hour=9, minute=0)},
            {"end_time": datetime(year=2019, month=1, day=9, hour=23, minute=0)}]
        expected = [
            [
                {"start_time": datetime(year=2019, month=1, day=1, hour=3, minute=0),
                 "end_time": datetime(year=2019, month=1, day=1, hour=3, minute=0)},
                {"end_time": datetime(year=2019, month=1, day=1, hour=8, minute=0)},
                {"end_time": datetime(year=2019, month=1, day=1, hour=12, minute=0)},
                {"end_time": datetime(year=2019, month=1, day=1, hour=22, minute=0)},
                {"end_time": datetime(year=2019, month=1, day=2, hour=3, minute=0)}
            ], [
                {"end_time": datetime(year=2019, month=1, day=2, hour=8, minute=0)},
                {"end_time": datetime(year=2019, month=1, day=2, hour=14, minute=0)}
            ], [
                {"end_time": datetime(year=2019, month=1, day=7, hour=8, minute=0)},
                {"end_time": datetime(year=2019, month=1, day=7, hour=13, minute=0)}
            ], [
                {"end_time": datetime(year=2019, month=1, day=8, hour=9, minute=0)}
            ], [
                {"end_time": datetime(year=2019, month=1, day=9, hour=23, minute=0)}
            ]
        ]
        result = split_days(data)
        self.assertEqual(len(result), len(expected))
        for i, day in enumerate(result):
            self.assertEqual(len(day), len(expected[i]))
            for j, meal in enumerate(day):
                for key in meal.keys():
                    self.assertEqual(meal[key], expected[i][j][key])


class TestExtractSnacks(unittest.TestCase):
    def test_normal_day(self):
        data = [
            {'name': "Frühstück", 'items': [
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                    "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                    "name": "Müsli", "calories": 230
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                    "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                    "name": "Milch", "calories": 97.37
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=11, minute=1),
                    "end_time": datetime(year=2019, month=1, day=1, hour=11, minute=1),
                    "name": "Keks", "calories": 40
                }
            ]},
            {'name': "Mittagessen", 'items': [
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                    "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                    "name": "Schnitzel", "calories": 176.3
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                    "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                    "name": "Pommes", "calories": 237.689
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                    "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                    "name": "Salat", "calories": 27.4567
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=14, minute=0),
                    "end_time": datetime(year=2019, month=1, day=1, hour=14, minute=0),
                    "name": "Studentenfutter", "calories": 130
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=14, minute=2),
                    "end_time": datetime(year=2019, month=1, day=1, hour=14, minute=2),
                    "name": "Bounty", "calories": 110
                }
            ]},
            {'name': "Abendessen", 'items': [
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=17, minute=0),
                    "end_time": datetime(year=2019, month=1, day=1, hour=17, minute=0),
                    "name": "Cookie", "calories": 112
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                    "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                    "name": "Brot", "calories": 167
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                    "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                    "name": "Wurst", "calories": 81.2
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=22, minute=18),
                    "end_time": datetime(year=2019, month=1, day=1, hour=22, minute=18),
                    "name": "Praline", "calories": 39.7
                }
            ]}
        ]
        expected = [
            {'name': "Frühstück", 'items': [
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                    "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=0),
                    "name": "Müsli", "calories": 230
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                    "end_time": datetime(year=2019, month=1, day=1, hour=9, minute=1),
                    "name": "Milch", "calories": 97.37
                }
            ]},
            {'name': "Vormittags-Snack", 'items': [
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=11, minute=1),
                    "end_time": datetime(year=2019, month=1, day=1, hour=11, minute=1),
                    "name": "Keks", "calories": 40
                }
            ]},
            {'name': "Mittagessen", 'items': [
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                    "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=30),
                    "name": "Schnitzel", "calories": 176.3
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                    "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=31),
                    "name": "Pommes", "calories": 237.689
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                    "end_time": datetime(year=2019, month=1, day=1, hour=12, minute=32),
                    "name": "Salat", "calories": 27.4567
                }
            ]},
            {'name': "Nachmittags-Snack", 'items': [
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=14, minute=0),
                    "end_time": datetime(year=2019, month=1, day=1, hour=14, minute=0),
                    "name": "Studentenfutter", "calories": 130
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=14, minute=2),
                    "end_time": datetime(year=2019, month=1, day=1, hour=14, minute=2),
                    "name": "Bounty", "calories": 110
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=17, minute=0),
                    "end_time": datetime(year=2019, month=1, day=1, hour=17, minute=0),
                    "name": "Cookie", "calories": 112
                }
            ]},
            {'name': "Abendessen", 'items': [
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                    "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=0),
                    "name": "Brot", "calories": 167
                },
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                    "end_time": datetime(year=2019, month=1, day=1, hour=19, minute=1),
                    "name": "Wurst", "calories": 81.2
                }
            ]},
            {'name': "Betthupferl", 'items': [
                {
                    "start_time": datetime(year=2019, month=1, day=1, hour=22, minute=18),
                    "end_time": datetime(year=2019, month=1, day=1, hour=22, minute=18),
                    "name": "Praline", "calories": 39.7
                }
            ]}
        ]
        translator = Translator('de', base_path='..')
        extracted = extract_snacks(data, translator)
        self.assertEqual(len(extracted), len(expected))
        for i, meal in enumerate(extracted):
            self.assertEqual(len(meal['items']), len(expected[i]['items']))
            self.assertEqual(meal['name'], expected[i]['name'])
            for j, item in enumerate(meal['items']):
                self.assertEqual(item['name'], expected[i]['items'][j]['name'])
                for key in expected[i]['items'][j].keys():
                    self.assertEqual(item[key], expected[i]['items'][j][key])
