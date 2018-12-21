#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from datetime import datetime

guesser_data = (57.6, 1.71, 33.9, 0)
activity_data = [
    {"activity": "Sleeping", "activity_no": 72,
     "start_time": datetime(year=2018, month=12, day=18, hour=0, minute=0),
     "end_time": datetime(year=2018, month=12, day=18, hour=8, minute=23)},
    {"activity": "Interval Training", "activity_no": 115,
     "start_time": datetime(year=2018, month=12, day=18, hour=8, minute=30),
     "end_time": datetime(year=2018, month=12, day=18, hour=8, minute=57)},
    {"activity": "Biking*", "activity_no": 1,
     "start_time": datetime(year=2018, month=12, day=18, hour=10, minute=30),
     "end_time": datetime(year=2018, month=12, day=18, hour=10, minute=42)},
    {"activity": "Walking*", "activity_no": 7,
     "start_time": datetime(year=2018, month=12, day=18, hour=12, minute=35),
     "end_time": datetime(year=2018, month=12, day=18, hour=12, minute=58)},
    {"activity": "Biking*", "activity_no": 1,
     "start_time": datetime(year=2018, month=12, day=18, hour=19, minute=30),
     "end_time": datetime(year=2018, month=12, day=18, hour=19, minute=53)},
    {"activity": "Dancing", "activity_no": 24,
     "start_time": datetime(year=2018, month=12, day=18, hour=20, minute=5),
     "end_time": datetime(year=2018, month=12, day=18, hour=21, minute=17)},
    {"activity": "Biking*", "activity_no": 1,
     "start_time": datetime(year=2018, month=12, day=18, hour=21, minute=45),
     "end_time": datetime(year=2018, month=12, day=18, hour=21, minute=57)},
    {"activity": "Sleeping", "activity_no": 72,
     "start_time": datetime(year=2018, month=12, day=18, hour=23, minute=50),
     "end_time": datetime(year=2018, month=12, day=19, hour=0, minute=0)}
]
weight_data = [
    (datetime(year=2018, month=10, day=5, hour=8, minute=42), 61.2),
    (datetime(year=2018, month=10, day=18, hour=9, minute=59), 60.5),
    (datetime(year=2018, month=11, day=2, hour=12, minute=30), 59.9),
    (datetime(year=2018, month=11, day=12, hour=7, minute=12), 59.2),
    (datetime(year=2018, month=11, day=20, hour=8, minute=48), 58.4),
    (datetime(year=2018, month=11, day=28, hour=8, minute=13), 59.6),
    (datetime(year=2018, month=12, day=3, hour=21, minute=55), 59),
    (datetime(year=2018, month=12, day=8, hour=9, minute=16), 57.8),
    (datetime(year=2018, month=12, day=17, hour=8, minute=32), 58.2),
    (datetime(year=2018, month=12, day=18, hour=8, minute=32), 59.2),
    (datetime(year=2018, month=12, day=19, hour=8, minute=32), 57.9),
    (datetime(year=2018, month=12, day=20, hour=8, minute=32), 58.1),
    (datetime(year=2018, month=12, day=21, hour=8, minute=32), 58.6),
    (datetime(year=2018, month=12, day=22, hour=8, minute=32), 58.4),
    (datetime(year=2018, month=12, day=23, hour=8, minute=32), 57.7),
    (datetime(year=2018, month=12, day=24, hour=8, minute=32), 59.1)
]
