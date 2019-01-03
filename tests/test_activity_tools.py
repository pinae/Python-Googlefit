#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from tests.test_data import activity_data
from activity_tools import activities_to_days, fill_day_with_unknown, clean_activities
from datetime import datetime
import unittest


class TestActivitiesToDays(unittest.TestCase):
    def test_unmodified_day(self):
        day = activity_data
        days = activities_to_days(day)
        for i, activity in enumerate(day):
            self.assertEqual(activity['activity'], days[0][i]['activity'])
            self.assertEqual(activity['activity_no'], days[0][i]['activity_no'])
            self.assertEqual(activity['start_time'], days[0][i]['start_time'])
            self.assertEqual(activity['end_time'], days[0][i]['end_time'])

    def test_long_activity(self):
        activities = [
            {"activity": "Biking*", "activity_no": 1,
             "start_time": datetime(year=2018, month=12, day=15, hour=19, minute=0),
             "end_time": datetime(year=2018, month=12, day=18, hour=10, minute=42)},
            {"activity": "Walking*", "activity_no": 7,
             "start_time": datetime(year=2018, month=12, day=18, hour=12, minute=35),
             "end_time": datetime(year=2018, month=12, day=18, hour=12, minute=58)},
            {"activity": "Biking*", "activity_no": 1,
             "start_time": datetime(year=2018, month=12, day=18, hour=19, minute=30),
             "end_time": datetime(year=2018, month=12, day=19, hour=10, minute=0)}
        ]
        days = activities_to_days(activities)
        self.assertEqual(len(days), 4)
        self.assertEqual(len(days[0]), 1)
        self.assertEqual(len(days[1]), 1)
        self.assertEqual(len(days[2]), 3)
        self.assertEqual(len(days[3]), 1)
        expected_activities = [
            [
                {"activity": "Biking*", "activity_no": 1,
                 "start_time": datetime(year=2018, month=12, day=16, hour=0, minute=0),
                 "end_time": datetime(year=2018, month=12, day=17, hour=0, minute=0)}
            ],
            [
                {"activity": "Biking*", "activity_no": 1,
                 "start_time": datetime(year=2018, month=12, day=17, hour=0, minute=0),
                 "end_time": datetime(year=2018, month=12, day=18, hour=0, minute=0)}
            ],
            [
                {"activity": "Biking*", "activity_no": 1,
                 "start_time": datetime(year=2018, month=12, day=18, hour=0, minute=0),
                 "end_time": datetime(year=2018, month=12, day=18, hour=10, minute=42)},
                {"activity": "Walking*", "activity_no": 7,
                 "start_time": datetime(year=2018, month=12, day=18, hour=12, minute=35),
                 "end_time": datetime(year=2018, month=12, day=18, hour=12, minute=58)},
                {"activity": "Biking*", "activity_no": 1,
                 "start_time": datetime(year=2018, month=12, day=18, hour=19, minute=30),
                 "end_time": datetime(year=2018, month=12, day=19, hour=0, minute=0)}
            ],
            [
                {"activity": "Biking*", "activity_no": 1,
                 "start_time": datetime(year=2018, month=12, day=19, hour=0, minute=0),
                 "end_time": datetime(year=2018, month=12, day=19, hour=10, minute=0)}
            ]
        ]
        for day_no, day in enumerate(expected_activities):
            for i, activity in enumerate(day):
                self.assertEqual(activity['activity'], days[day_no][i]['activity'])
                self.assertEqual(activity['activity_no'], days[day_no][i]['activity_no'])
                self.assertEqual(activity['start_time'], days[day_no][i]['start_time'])
                self.assertEqual(activity['end_time'], days[day_no][i]['end_time'])


class TestFillDayWithBmr(unittest.TestCase):
    def test_fill_day_with_unknown(self):
        full_day = fill_day_with_unknown(activity_data)
        expected_day = [
            {"activity": "Sleeping", "activity_no": 72,
             "start_time": datetime(year=2018, month=12, day=18, hour=0, minute=0),
             "end_time": datetime(year=2018, month=12, day=18, hour=8, minute=23)},
            {"activity": "Unknown (unable to detect activity)*", "activity_no": 4,
             "start_time": datetime(year=2018, month=12, day=18, hour=8, minute=23),
             "end_time": datetime(year=2018, month=12, day=18, hour=8, minute=30)},
            {"activity": "Interval Training", "activity_no": 115,
             "start_time": datetime(year=2018, month=12, day=18, hour=8, minute=30),
             "end_time": datetime(year=2018, month=12, day=18, hour=8, minute=57)},
            {"activity": "Unknown (unable to detect activity)*", "activity_no": 4,
             "start_time": datetime(year=2018, month=12, day=18, hour=8, minute=57),
             "end_time": datetime(year=2018, month=12, day=18, hour=10, minute=30)},
            {"activity": "Biking*", "activity_no": 1,
             "start_time": datetime(year=2018, month=12, day=18, hour=10, minute=30),
             "end_time": datetime(year=2018, month=12, day=18, hour=10, minute=42)},
            {"activity": "Unknown (unable to detect activity)*", "activity_no": 4,
             "start_time": datetime(year=2018, month=12, day=18, hour=10, minute=42),
             "end_time": datetime(year=2018, month=12, day=18, hour=12, minute=35)},
            {"activity": "Walking*", "activity_no": 7,
             "start_time": datetime(year=2018, month=12, day=18, hour=12, minute=35),
             "end_time": datetime(year=2018, month=12, day=18, hour=12, minute=58)},
            {"activity": "Unknown (unable to detect activity)*", "activity_no": 4,
             "start_time": datetime(year=2018, month=12, day=18, hour=12, minute=58),
             "end_time": datetime(year=2018, month=12, day=18, hour=19, minute=30)},
            {"activity": "Biking*", "activity_no": 1,
             "start_time": datetime(year=2018, month=12, day=18, hour=19, minute=30),
             "end_time": datetime(year=2018, month=12, day=18, hour=19, minute=53)},
            {"activity": "Unknown (unable to detect activity)*", "activity_no": 4,
             "start_time": datetime(year=2018, month=12, day=18, hour=19, minute=53),
             "end_time": datetime(year=2018, month=12, day=18, hour=20, minute=5)},
            {"activity": "Dancing", "activity_no": 24,
             "start_time": datetime(year=2018, month=12, day=18, hour=20, minute=5),
             "end_time": datetime(year=2018, month=12, day=18, hour=21, minute=17)},
            {"activity": "Unknown (unable to detect activity)*", "activity_no": 4,
             "start_time": datetime(year=2018, month=12, day=18, hour=21, minute=17),
             "end_time": datetime(year=2018, month=12, day=18, hour=21, minute=45)},
            {"activity": "Biking*", "activity_no": 1,
             "start_time": datetime(year=2018, month=12, day=18, hour=21, minute=45),
             "end_time": datetime(year=2018, month=12, day=18, hour=21, minute=57)},
            {"activity": "Unknown (unable to detect activity)*", "activity_no": 4,
             "start_time": datetime(year=2018, month=12, day=18, hour=21, minute=57),
             "end_time": datetime(year=2018, month=12, day=18, hour=23, minute=50)},
            {"activity": "Sleeping", "activity_no": 72,
             "start_time": datetime(year=2018, month=12, day=18, hour=23, minute=50),
             "end_time": datetime(year=2018, month=12, day=19, hour=0, minute=0)}
        ]
        self.assertEqual(len(full_day), len(expected_day))
        for i, activity in enumerate(expected_day):
            self.assertEqual(activity['activity'], full_day[i]['activity'])
            self.assertEqual(activity['activity_no'], full_day[i]['activity_no'])
            self.assertEqual(activity['start_time'], full_day[i]['start_time'])
            self.assertEqual(activity['end_time'], full_day[i]['end_time'])


class TestCleanActivities(unittest.TestCase):
    def test_no_cutting_needed(self):
        cleaned_activities = clean_activities(activity_data)
        self.assertEqual(len(activity_data), len(cleaned_activities))
        for i, activity in enumerate(activity_data):
            self.assertEqual(activity['activity'], cleaned_activities[i]['activity'])
            self.assertEqual(activity['activity_no'], cleaned_activities[i]['activity_no'])
            self.assertEqual(activity['start_time'], cleaned_activities[i]['start_time'])
            self.assertEqual(activity['end_time'], cleaned_activities[i]['end_time'])

    def test_cutting_and_deleting(self):
        manipulated_activities = activity_data.copy()
        manipulated_activities.insert(
            3, {"activity": "Unknown (unable to detect activity)*", "activity_no": 4,
                "start_time": datetime(year=2018, month=12, day=18, hour=10, minute=35),
                "end_time": datetime(year=2018, month=12, day=18, hour=11, minute=42)})
        manipulated_activities.insert(
            7, {"activity": "Unknown (unable to detect activity)*", "activity_no": 4,
                "start_time": datetime(year=2018, month=12, day=18, hour=20, minute=30),
                "end_time": datetime(year=2018, month=12, day=18, hour=21, minute=10)})
        cleaned_activities = clean_activities(manipulated_activities)
        expected_activities = manipulated_activities.copy()
        del expected_activities[7]
        expected_activities[3]["start_time"] = datetime(year=2018, month=12, day=18, hour=10, minute=42)
        self.assertEqual(len(expected_activities), len(cleaned_activities))
        for i, activity in enumerate(expected_activities):
            self.assertEqual(activity['activity'], cleaned_activities[i]['activity'])
            self.assertEqual(activity['activity_no'], cleaned_activities[i]['activity_no'])
            self.assertEqual(activity['start_time'], cleaned_activities[i]['start_time'])
            self.assertEqual(activity['end_time'], cleaned_activities[i]['end_time'])


if __name__ == '__main__':
    unittest.main()
