#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics, QPolygon, QPainterPath
from PyQt5.QtCore import QPoint, QPointF
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta
from math import ceil, trunc


class TimedDigram(QWidget, object):
    class WrongDataFormatException(Exception):
        pass

    def __init__(self, padding=4, y_unit="kg", y_format="{:3.0f}", *args):
        super(TimedDigram, self).__init__(*args)
        self.padding = padding
        self.y_unit = y_unit
        self.data = []
        self.x_range = datetime.now(), datetime.now()
        self.y_range = 0.0, 0.0
        self.y_format = y_format
        self.gray_line_color = QColor(140, 140, 140)
        self.axis_number_color = QColor(0, 0, 0)
        self.gray_pen = QPen(self.gray_line_color, 1, Qt.SolidLine)
        self.text_pen = QPen(self.axis_number_color, 1, Qt.SolidLine)
        self.gray_brush = QBrush(self.gray_line_color)
        self.font = QFont("Helvetica", pointSize=8, weight=0, italic=0)
        self.fm = QFontMetrics(self.font)

    def paintEvent(self, *args):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.TextAntialiasing, True)
        qp.setRenderHint(QPainter.Antialiasing, True)
        self.draw(qp)
        qp.end()

    def draw(self, qp):
        size = self.size()
        self.draw_x_axis(qp, size)
        self.draw_y_axis(qp, size)

    def draw_x_axis(self, qp, size):
        qp.setPen(self.gray_pen)
        qp.setBrush(self.gray_brush)
        unit_text_width = self.fm.size(Qt.TextSingleLine, self.y_unit).width()
        time_text_height = self.fm.size(Qt.TextSingleLine, "12:00").height()
        qp.drawLine(self.padding + unit_text_width + 1 - 4,
                    size.height() - time_text_height - self.padding,
                    size.width() - self.padding,
                    size.height() - time_text_height - self.padding)
        polygon = QPolygon()
        polygon.append(QPoint(size.width() - self.padding,
                              size.height() - time_text_height - self.padding))
        polygon.append(QPoint(size.width() - self.padding - 6,
                              size.height() - time_text_height - self.padding + 4))
        polygon.append(QPoint(size.width() - self.padding - 6,
                              size.height() - time_text_height - self.padding - 4))
        qp.drawPolygon(polygon, fillRule=Qt.WindingFill)
        self.draw_x_axis_labels(qp, size, unit_text_width, time_text_height)

    def draw_y_axis(self, qp, size):
        qp.setPen(self.gray_pen)
        qp.setBrush(self.gray_brush)
        unit_text_width = self.fm.size(Qt.TextSingleLine, self.y_unit).width()
        time_text_height = self.fm.size(Qt.TextSingleLine, "12:00").height()
        qp.drawLine(self.padding + unit_text_width + 1,
                    size.height() - time_text_height + 4 - self.padding,
                    self.padding + unit_text_width + 1,
                    self.padding)
        polygon = QPolygon()
        polygon.append(QPoint(self.padding + unit_text_width + 1,
                              self.padding))
        polygon.append(QPoint(self.padding + unit_text_width + 1 - 4,
                              self.padding + 6))
        polygon.append(QPoint(self.padding + unit_text_width + 1 + 4,
                              self.padding + 6))
        qp.drawPolygon(polygon, fillRule=Qt.WindingFill)
        self.draw_y_axis_labels(qp, size, unit_text_width, time_text_height)
        qp.setFont(self.font)
        qp.setPen(self.text_pen)
        qp.drawText(self.padding, self.padding + 15, self.y_unit)

    def draw_x_axis_labels(self, qp, size, unit_text_width, time_text_height):
        qp.setFont(self.font)
        available_x_distance = size.width() - self.padding - 6 - (
                self.padding + unit_text_width + 1)
        display_hours = (self.x_range[1] - self.x_range[0]) < timedelta(days=1, hours=3)
        if display_hours:
            current_tick = datetime(year=self.x_range[0].year, month=self.x_range[0].month, day=self.x_range[0].day,
                                    hour=self.x_range[0].hour + 1)

        else:
            current_tick = datetime(year=self.x_range[0].year, month=self.x_range[0].month, day=self.x_range[0].day + 1)
        x_tick_pos = self.padding + unit_text_width + 1 + (
            (current_tick - self.x_range[0]) / (self.x_range[1] - self.x_range[0]) * available_x_distance)
        qp.setPen(self.gray_pen)
        qp.drawLine(x_tick_pos, size.height() - time_text_height - self.padding - 3,
                    x_tick_pos, size.height() - time_text_height - self.padding + 7)
        qp.setPen(self.text_pen)
        if display_hours:
            current_text = current_tick.strftime("%H:%M")
        else:
            current_text = current_tick.strftime("%d.%m.")
        current_text_width = self.fm.size(Qt.TextSingleLine, current_text).width()
        qp.drawText(x_tick_pos - current_text_width // 2,
                    size.height() - self.padding,
                    current_text)
        current_text_end = x_tick_pos + current_text_width // 2
        if display_hours:
            current_tick = current_tick + timedelta(hours=1)
        else:
            current_tick = current_tick + timedelta(days=1)
        while current_tick < self.x_range[1]:
            qp.setPen(self.gray_pen)
            x_tick_pos = self.padding + unit_text_width + 1 + (
                (current_tick - self.x_range[0]) / (self.x_range[1] - self.x_range[0]) * available_x_distance)
            if x_tick_pos - current_text_width * 1.1 > current_text_end and \
                    x_tick_pos + current_text_width // 2 <= size.width() - self.padding:
                qp.drawLine(x_tick_pos, size.height() - time_text_height - self.padding - 3,
                            x_tick_pos, size.height() - time_text_height - self.padding + 7)
            else:
                qp.drawLine(x_tick_pos, size.height() - time_text_height - self.padding - 3,
                            x_tick_pos, size.height() - time_text_height - self.padding + 3)
            if display_hours:
                current_text = current_tick.strftime("%H:%M")
            else:
                current_text = current_tick.strftime("%d.%m.")
            current_text_width = self.fm.size(Qt.TextSingleLine, current_text).width()
            if x_tick_pos - current_text_width * 1.1 > current_text_end and \
                    x_tick_pos + current_text_width // 2 <= size.width() - self.padding:
                qp.setPen(self.text_pen)
                qp.drawText(x_tick_pos - current_text_width // 2,
                            size.height() - self.padding,
                            current_text)
                current_text_end = x_tick_pos + current_text_width // 2
            if display_hours:
                current_tick = current_tick + timedelta(hours=1)
            else:
                current_tick = current_tick + timedelta(days=1)

    def draw_y_axis_labels(self, qp, size, unit_text_width, time_text_height):
        qp.setFont(self.font)
        available_y_distance = size.height() - time_text_height + 4 - 2 * self.padding
        tick_distance = ceil(time_text_height * (self.y_range[1] - self.y_range[0]) / available_y_distance)
        current_tick = ceil(self.y_range[0])
        y_tick_pos = size.height() - time_text_height - self.padding - (
                current_tick - self.y_range[0]) / (self.y_range[1] - self.y_range[0]) * available_y_distance
        current_text = self.y_format.format(current_tick)
        current_text_size = self.fm.size(Qt.TextSingleLine, current_text)
        qp.setPen(self.gray_pen)
        qp.drawLine(self.padding + unit_text_width + 1 - 3, y_tick_pos,
                    self.padding + unit_text_width + 1 + 3, y_tick_pos)
        qp.setPen(self.text_pen)
        qp.drawText(self.padding + unit_text_width + 1 - 3 - current_text_size.width(),
                    y_tick_pos + current_text_size.height() / 4,
                    current_text)
        current_tick_end = y_tick_pos - current_text_size.height() / 2
        current_tick = current_tick + tick_distance
        while current_tick < self.y_range[1]:
            qp.setPen(self.gray_pen)
            y_tick_pos = size.height() - time_text_height + 4 - self.padding - (
                    current_tick - self.y_range[0]) / (self.y_range[1] - self.y_range[0]) * available_y_distance
            current_text = self.y_format.format(current_tick)
            current_text_size = self.fm.size(Qt.TextSingleLine, current_text)
            qp.setPen(self.gray_pen)
            if current_tick_end >= y_tick_pos - current_text_size.height() // 2 > self.padding + 15:
                qp.drawLine(self.padding + unit_text_width + 1 - 3, y_tick_pos,
                            self.padding + unit_text_width + 1 + 3, y_tick_pos)
                qp.setPen(self.text_pen)
                qp.drawText(self.padding + unit_text_width + 1 - 3 -
                            current_text_size.width(),
                            y_tick_pos + current_text_size.height() / 4,
                            current_text)
                current_tick_end = y_tick_pos - current_text_size.height() / 2
            else:
                qp.drawLine(self.padding + unit_text_width + 1 - 3, y_tick_pos,
                            self.padding + unit_text_width + 1 + 3, y_tick_pos)
            current_tick = current_tick + tick_distance


class TimedLineChart(TimedDigram):
    def __init__(self, padding=4, y_unit="kg", y_format="{:3.0f}", *args):
        super(TimedLineChart, self).__init__(padding=padding, y_unit=y_unit, y_format=y_format, *args)
        self.data_color = QColor(140, 140, 255)
        self.smooth_curve_color = QColor(0, 0, 230)
        self.smooth_factor = 0.5

    def set_data(self, data):
        if len(data) > 0:
            if len(data[0]) != 2 or type(data[0][0]) is not datetime or (
                    type(data[0][1]) is not int and type(data[0][1]) is not float):
                raise TimedLineChart.WrongDataFormatException
            min_x = data[0][0]
            max_x = data[0][0]
            min_y = data[0][1]
            max_y = data[0][1]
            for point in data:
                min_x = min(min_x, point[0])
                max_x = max(max_x, point[0])
                min_y = min(min_y, point[1])
                max_y = max(max_y, point[1])
            self.x_range = min_x, max_x
            self.y_range = min_y, max_y
        else:
            self.x_range = datetime.now(), datetime.now()
            self.y_range = 0.0, 0.0
        self.data = data

    def draw(self, qp):
        size = self.size()
        self.draw_x_axis(qp, size)
        self.draw_y_axis(qp, size)
        self.draw_data(qp, size)

    def draw_data(self, qp, size):
        point_pen = QPen(self.data_color, 1, Qt.SolidLine)
        qp.setPen(point_pen)
        qp.setBrush(QBrush(self.data_color))
        unit_text_width = self.fm.size(Qt.TextSingleLine, self.y_unit).width()
        time_text_height = self.fm.size(Qt.TextSingleLine, "12:00").height()
        available_x_distance = size.width() - self.padding - 6 - (
                self.padding + unit_text_width + 1)
        available_y_distance = size.height() - time_text_height - 2 * self.padding
        last_point = None
        for time, value in self.data:
            x_pos = self.padding + unit_text_width + 1 + (
                (time - self.x_range[0]) / (self.x_range[1] - self.x_range[0]) * available_x_distance)
            y_pos = size.height() - time_text_height - self.padding - (
                value - self.y_range[0]) / (self.y_range[1] - self.y_range[0]) * available_y_distance
            qp.drawEllipse(x_pos-2, y_pos-2, 4, 4)
            if last_point is not None:
                qp.drawLine(last_point[0], last_point[1], x_pos, y_pos)
            last_point = x_pos, y_pos
        if len(self.data) > 2:
            smooth_value = self.data[0][1]
            current_point_index = 1
            path = QPainterPath()
            path.moveTo(self.padding + unit_text_width + 1,
                        size.height() - time_text_height - self.padding - (
                            smooth_value - self.y_range[0]) / (self.y_range[1] - self.y_range[0]) *
                        available_y_distance)
            for i in range(available_x_distance):
                x = self.x_range[0] + i / available_x_distance * (self.x_range[1] - self.x_range[0])
                while self.data[current_point_index][0] < x:
                    current_point_index += 1
                point_factor = (x - self.data[current_point_index - 1][0]) / (
                    self.data[current_point_index][0] - self.data[current_point_index - 1][0])
                time_slice = (self.x_range[1] - self.x_range[0]) / available_x_distance
                smooth_value = (smooth_value * (1 - self.smooth_factor * time_slice / timedelta(days=1)) +
                                self.smooth_factor * time_slice / timedelta(days=1) * (
                                    self.data[current_point_index][1] * point_factor +
                                    self.data[current_point_index - 1][1] * (1 - point_factor)))
                path.lineTo(
                    self.padding + unit_text_width + 1 + (
                        (x - self.x_range[0]) / (self.x_range[1] - self.x_range[0]) * available_x_distance),
                    size.height() - time_text_height - self.padding - (
                        smooth_value - self.y_range[0]) / (self.y_range[1] - self.y_range[0]) * available_y_distance
                )
            qp.setPen(QPen(self.smooth_curve_color, 2, Qt.SolidLine))
            qp.setBrush(Qt.NoBrush)
            qp.drawPath(path)


class TimedActivityBlockDiagram(TimedDigram):
    def __init__(self, calorie_guesser, padding=4, y_unit="kcal/h", y_format="{:3.0f}", *args):
        super(TimedActivityBlockDiagram, self).__init__(padding=padding, y_unit=y_unit, y_format=y_format, *args)
        self.setMinimumHeight(50)
        self.setMinimumWidth(100)
        self.calorie_guesser = calorie_guesser
        self.inactive_pen_color = QColor(212, 175, 0)
        self.inactive_brush_color = QColor(236, 207, 71)
        self.sleep_pen_color = QColor(0, 0, 230)
        self.sleep_brush_color = QColor(140, 140, 255)
        self.light_activity_pen_color = QColor(0, 175, 66)
        self.light_activity_brush_color = QColor(71, 236, 133)
        self.heavy_activity_pen_color = QColor(198, 0, 37)
        self.heavy_activity_brush_color = QColor(233, 50, 85)
        self.inactive_pen = QPen(self.inactive_pen_color, 1, Qt.SolidLine)
        self.inactive_brush = QBrush(self.inactive_brush_color)
        self.sleep_pen = QPen(self.sleep_pen_color, 1, Qt.SolidLine)
        self.sleep_brush = QBrush(self.sleep_brush_color)
        self.light_activity_pen = QPen(self.light_activity_pen_color, 1, Qt.SolidLine)
        self.light_activity_brush = QBrush(self.light_activity_brush_color)
        self.heavy_activity_pen = QPen(self.heavy_activity_pen_color, 1, Qt.SolidLine)
        self.heavy_activity_brush = QBrush(self.heavy_activity_brush_color)
        self.x_range = datetime.now(), datetime.now()
        self.y_range = 0.0, 100.0
        self.data = []
        self.calorie_estimates = []

    def get_color_for_activity(self, activity_number):
        activity_map = {
            9: (self.heavy_activity_pen, self.heavy_activity_brush),
            119: (self.light_activity_pen, self.light_activity_brush),
            10: (self.light_activity_pen, self.light_activity_brush),
            11: (self.light_activity_pen, self.light_activity_brush),
            12: (self.light_activity_pen, self.light_activity_brush),
            13: (self.heavy_activity_pen, self.heavy_activity_brush),
            1: (self.light_activity_pen, self.light_activity_brush),
            14: (self.light_activity_pen, self.light_activity_brush),
            15: (self.light_activity_pen, self.light_activity_brush),
            16: (self.light_activity_pen, self.light_activity_brush),
            17: (self.light_activity_pen, self.light_activity_brush),
            18: (self.light_activity_pen, self.light_activity_brush),
            19: (self.light_activity_pen, self.light_activity_brush),
            20: (self.light_activity_pen, self.light_activity_brush),
            21: (self.heavy_activity_pen, self.heavy_activity_brush),
            22: (self.heavy_activity_pen, self.heavy_activity_brush),
            23: (self.light_activity_pen, self.light_activity_brush),
            113: (self.heavy_activity_pen, self.heavy_activity_brush),
            106: (self.light_activity_pen, self.light_activity_brush),
            24: (self.light_activity_pen, self.light_activity_brush),
            102: (self.light_activity_pen, self.light_activity_brush),
            25: (self.light_activity_pen, self.light_activity_brush),
            103: (self.light_activity_pen, self.light_activity_brush),
            26: (self.light_activity_pen, self.light_activity_brush),
            27: (self.light_activity_pen, self.light_activity_brush),
            28: (self.light_activity_pen, self.light_activity_brush),
            29: (self.light_activity_pen, self.light_activity_brush),
            30: (self.light_activity_pen, self.light_activity_brush),
            31: (self.light_activity_pen, self.light_activity_brush),
            32: (self.light_activity_pen, self.light_activity_brush),
            33: (self.heavy_activity_pen, self.heavy_activity_brush),
            34: (self.light_activity_pen, self.light_activity_brush),
            114: (self.heavy_activity_pen, self.heavy_activity_brush),
            35: (self.light_activity_pen, self.light_activity_brush),
            36: (self.light_activity_pen, self.light_activity_brush),
            37: (self.light_activity_pen, self.light_activity_brush),
            104: (self.light_activity_pen, self.light_activity_brush),
            115: (self.heavy_activity_pen, self.heavy_activity_brush),
            39: (self.heavy_activity_pen, self.heavy_activity_brush),
            40: (self.heavy_activity_pen, self.heavy_activity_brush),
            41: (self.heavy_activity_pen, self.heavy_activity_brush),
            42: (self.light_activity_pen, self.light_activity_brush),
            43: (self.heavy_activity_pen, self.heavy_activity_brush),
            44: (self.light_activity_pen, self.light_activity_brush),
            45: (self.sleep_pen, self.sleep_brush),
            46: (self.light_activity_pen, self.light_activity_brush),
            2: (self.light_activity_pen, self.light_activity_brush),
            47: (self.heavy_activity_pen, self.heavy_activity_brush),
            48: (self.light_activity_pen, self.light_activity_brush),
            49: (self.light_activity_pen, self.light_activity_brush),
            50: (self.light_activity_pen, self.light_activity_brush),
            51: (self.light_activity_pen, self.light_activity_brush),
            52: (self.heavy_activity_pen, self.heavy_activity_brush),
            53: (self.heavy_activity_pen, self.heavy_activity_brush),
            54: (self.heavy_activity_pen, self.heavy_activity_brush),
            55: (self.light_activity_pen, self.light_activity_brush),
            8: (self.heavy_activity_pen, self.heavy_activity_brush),
            56: (self.heavy_activity_pen, self.heavy_activity_brush),
            57: (self.heavy_activity_pen, self.heavy_activity_brush),
            58: (self.heavy_activity_pen, self.heavy_activity_brush),
            59: (self.light_activity_pen, self.light_activity_brush),
            60: (self.light_activity_pen, self.light_activity_brush),
            61: (self.light_activity_pen, self.light_activity_brush),
            62: (self.light_activity_pen, self.light_activity_brush),
            63: (self.light_activity_pen, self.light_activity_brush),
            105: (self.light_activity_pen, self.light_activity_brush),
            64: (self.light_activity_pen, self.light_activity_brush),
            65: (self.light_activity_pen, self.light_activity_brush),
            66: (self.light_activity_pen, self.light_activity_brush),
            67: (self.light_activity_pen, self.light_activity_brush),
            68: (self.light_activity_pen, self.light_activity_brush),
            69: (self.light_activity_pen, self.light_activity_brush),
            70: (self.light_activity_pen, self.light_activity_brush),
            71: (self.light_activity_pen, self.light_activity_brush),
            72: (self.sleep_pen, self.sleep_brush),
            109: (self.sleep_pen, self.sleep_brush),
            110: (self.sleep_pen, self.sleep_brush),
            111: (self.sleep_pen, self.sleep_brush),
            73: (self.light_activity_pen, self.light_activity_brush),
            75: (self.light_activity_pen, self.light_activity_brush),
            120: (self.light_activity_pen, self.light_activity_brush),
            76: (self.light_activity_pen, self.light_activity_brush),
            77: (self.heavy_activity_pen, self.heavy_activity_brush),
            78: (self.heavy_activity_pen, self.heavy_activity_brush),
            79: (self.light_activity_pen, self.light_activity_brush),
            80: (self.heavy_activity_pen, self.heavy_activity_brush),
            81: (self.heavy_activity_pen, self.heavy_activity_brush),
            82: (self.light_activity_pen, self.light_activity_brush),
            84: (self.light_activity_pen, self.light_activity_brush),
            83: (self.light_activity_pen, self.light_activity_brush),
            85: (self.light_activity_pen, self.light_activity_brush),
            86: (self.light_activity_pen, self.light_activity_brush),
            87: (self.light_activity_pen, self.light_activity_brush),
            88: (self.light_activity_pen, self.light_activity_brush),
            89: (self.light_activity_pen, self.light_activity_brush),
            90: (self.light_activity_pen, self.light_activity_brush),
            91: (self.light_activity_pen, self.light_activity_brush),
            92: (self.heavy_activity_pen, self.heavy_activity_brush),
            7: (self.light_activity_pen, self.light_activity_brush),
            93: (self.light_activity_pen, self.light_activity_brush),
            94: (self.light_activity_pen, self.light_activity_brush),
            95: (self.light_activity_pen, self.light_activity_brush),
            116: (self.light_activity_pen, self.light_activity_brush),
            96: (self.light_activity_pen, self.light_activity_brush),
            97: (self.heavy_activity_pen, self.heavy_activity_brush),
            98: (self.light_activity_pen, self.light_activity_brush),
            99: (self.heavy_activity_pen, self.heavy_activity_brush),
            100: (self.light_activity_pen, self.light_activity_brush),
            101: (self.heavy_activity_pen, self.heavy_activity_brush)
        }
        if activity_number in activity_map.keys():
            return activity_map[activity_number]
        else:
            return self.inactive_pen, self.inactive_brush

    def set_data(self, data):
        if len(data) > 0:
            self.calorie_estimates = []
            for point in data:
                if 'activity_no' not in point or type(point['activity_no']) is not int or \
                        'start_time' not in point or type(point['start_time']) is not datetime or \
                        'end_time' not in point or type(point['end_time']) is not datetime:
                    raise TimedActivityBlockDiagram.WrongDataFormatException
                self.calorie_estimates.append(self.calorie_guesser.guess_kcal(point))
            min_x = data[0]['start_time']
            max_x = data[0]['end_time']
            min_y = 0
            max_y = self.calorie_estimates[0] * timedelta(hours=1) / (data[0]['end_time'] - data[0]['start_time'])
            for i, point in enumerate(data):
                min_x = min(min_x, point['start_time'])
                max_x = max(max_x, point['end_time'])
                min_y = min(min_y, self.calorie_estimates[i] *
                            timedelta(hours=1) / (point['end_time'] - point['start_time']))
                max_y = max(max_y, self.calorie_estimates[i] *
                            timedelta(hours=1) / (point['end_time'] - point['start_time']))
            self.x_range = min_x, max_x
            self.y_range = min_y, max_y
        else:
            self.x_range = datetime.now(), datetime.now()
            self.y_range = 0.0, 100.0
        self.data = data

    def draw(self, qp):
        size = self.size()
        self.draw_x_axis(qp, size)
        self.draw_y_axis(qp, size)
        self.draw_data(qp, size)

    def draw_data(self, qp, size):
        unit_text_width = self.fm.size(Qt.TextSingleLine, self.y_unit).width()
        time_text_height = self.fm.size(Qt.TextSingleLine, "12:00").height()
        available_x_distance = size.width() - self.padding - 6 - (self.padding + unit_text_width + 1)
        available_y_distance = size.height() - time_text_height + 4 - 2 * self.padding
        for i, activity in enumerate(self.data):
            pen, brush = self.get_color_for_activity(activity['activity_no'])
            qp.setPen(pen)
            qp.setBrush(brush)
            height = available_y_distance * (
                    (self.calorie_estimates[i] * timedelta(hours=1) / (activity['end_time'] - activity['start_time']) -
                     self.y_range[0]) / (self.y_range[1] - self.y_range[0]))
            qp.drawRect(
                self.padding + unit_text_width + 1 + available_x_distance *
                ((activity['start_time'] - self.x_range[0]) / (self.x_range[1] - self.x_range[0])),
                size.height() - time_text_height - self.padding - height,
                available_x_distance *
                ((activity['end_time'] - activity['start_time']) / (self.x_range[1] - self.x_range[0])),
                height)
