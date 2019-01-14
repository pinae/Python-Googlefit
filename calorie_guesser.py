#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from datetime import datetime, timedelta


class CalorieGuesser(object):
    def __init__(self, mass=60, height=1.7, age=34, sex=0):
        self.mass = mass
        self.height = height
        self.age = age
        self.sex = sex
        self.bmr = self.mifflin_st_jeor_estimation()
        self.activity_met_map = {
            9: 6,
            119: 4.3,
            10: 6.5,
            11: 5.5,
            12: 11,
            13: 12,
            1: 8,
            14: 10,
            15: 12,
            16: 10,
            17: 10,
            18: 8,
            19: 7.1,
            20: 13.4,
            21: 4,
            22: 12,
            23: 6.1,
            113: 11,
            106: 4,
            24: 7,
            102: 11,
            117: 2,
            25: 12,
            103: 12,
            118: 2,
            26: 8,
            27: 6.5,
            28: 7.5,
            29: 10.3,
            30: 10,
            31: 4,
            32: 4.5,
            33: 7,
            34: 10,
            114: 13,
            35: 6,
            36: 12.9,
            37: 6.9,
            38: 3,
            104: 9.2,
            0: 2,
            115: 11,
            39: 12,
            40: 10,
            41: 11,
            42: 10,
            43: 8,
            44: 10,
            45: 1.5,
            46: 10,
            2: 3,
            108: 1.5,
            47: 5,
            48: 3.5,
            49: 4,
            50: 5,
            51: 10,
            52: 12,
            53: 13,
            54: 13,
            55: 12.6,
            8: 12,
            56: 8.8,
            57: 12.9,
            58: 12,
            59: 3.5,
            60: 11,
            61: 5,
            62: 9.2,
            63: 9,
            105: 9,
            64: 8,
            65: 7,
            66: 9,
            67: 9.9,
            68: 8,
            69: 9,
            70: 7,
            71: 8,
            72: 0.9,
            109: 1,
            110: 0.8,
            111: 0.9,
            112: 1.5,
            73: 8,
            74: 2.5,
            75: 9.5,
            120: 4.5,
            76: 10,
            77: 4.7,
            78: 5,
            79: 4.5,
            3: 1,
            80: 10,
            81: 11,
            82: 6.8,
            84: 11.5,
            83: 8.9,
            85: 4.7,
            86: 5,
            87: 6.8,
            5: 1,
            88: 11,
            4: 1,
            89: 6,
            90: 6,
            91: 6,
            92: 9,
            7: 3.2,
            93: 5.3,
            94: 5.3,
            95: 3.2,
            116: 3.2,
            96: 9.8,
            97: 10.9,
            98: 7,
            99: 8,
            100: 3.2,
            101: 5
        }

    def mifflin_st_jeor_estimation(self):
        # The last factor of 0.583 is because using mets and durations from a typical day results for me
        # in a bmr of 2753 which is way above the real bmr of ca. 1600. The formula clearly estimates a day
        # with physical activity with 1604kcal for me which is about the amount I can eat without
        # loosing or gaining weight. However for calculating the correct calorie counts for the
        # activities we need to have a base metabolic rate for calculating the calorie counts. This is why
        # I added this factor to the original formula.
        return 41.87 * self.mass + 26.17 * self.height - 20.93 * self.age - 161 + 166 * self.sex * 0.583

    def set_bmr(self, bmr):
        self.bmr = bmr

    def guess_kcal(self, activity):
        activity_duration = activity['end_time'] - activity['start_time']
        if activity['activity_no'] in self.activity_met_map.keys():
            return self.activity_met_map[activity['activity_no']] * self.bmr * (activity_duration / timedelta(hours=24))
        else:
            return self.bmr * (activity_duration / timedelta(hours=24))

    def set_height(self, height_in_m):
        self.height = height_in_m
        self.bmr = self.mifflin_st_jeor_estimation()

    def set_age(self, age_in_years):
        self.age = age_in_years
        self.bmr = self.mifflin_st_jeor_estimation()

    def set_birthdate(self, birthdate):
        age_delta = datetime.now() - birthdate
        self.set_age((age_delta.days + age_delta.seconds / (24 * 60 * 60)) / 365.24219)

    def set_weight(self, weight_in_kg):
        self.mass = weight_in_kg
        self.bmr = self.mifflin_st_jeor_estimation()

    def set_sex(self, sex):
        self.sex = sex
        self.bmr = self.mifflin_st_jeor_estimation()
