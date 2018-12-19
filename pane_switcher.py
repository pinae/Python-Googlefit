#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QColor
from PyQt5.QtSvg import QSvgWidget
from os import path


class PaneSelectItem(QWidget):
    paneSelected = pyqtSignal(QWidget)

    def __init__(self, icon_inactive_filename, icon_active_filename, icon_hover_filename, label_text=None):
        super(PaneSelectItem, self).__init__()
        self.setMouseTracking(True)
        self.setAutoFillBackground(True)
        self.active = False
        self.active_color = QColor(239, 0, 183)
        self.background_color = QColor(30, 30, 30)
        self.v_layout = QVBoxLayout()
        self.v_layout.addStretch()
        self.icon_layout = QHBoxLayout()
        self.icon_layout.addStretch()
        self.icon_inactive = QSvgWidget(icon_inactive_filename)
        self.set_icon_size(self.icon_inactive, 200, 43)
        self.icon_active = QSvgWidget(icon_active_filename)
        self.set_icon_size(self.icon_active, 200, 43)
        self.icon_hover = QSvgWidget(icon_hover_filename)
        self.set_icon_size(self.icon_hover, 200, 43)
        self.icon_layout.addWidget(self.icon_inactive)
        self.icon_layout.addStretch()
        self.v_layout.addLayout(self.icon_layout)
        if label_text is not None:
            self.label_layout = QHBoxLayout()
            self.label_layout.addStretch()
            self.label = QLabel()
            self.label.setStyleSheet("QLabel {color: #ffffff;}")
            self.label.setVisible(False)
            self.label.setText(label_text)
            self.label_layout.addWidget(self.label)
            self.label_layout.addStretch()
            self.v_layout.addLayout(self.label_layout)
        else:
            self.label = None
        self.v_layout.addStretch()
        self.setLayout(self.v_layout)

    @staticmethod
    def set_icon_size(svg_widget, width, height):
        svg_widget.setMaximumHeight(height)
        svg_widget.setMaximumWidth(width)
        svg_widget.setMinimumHeight(height)
        svg_widget.setMinimumWidth(width)

    def set_active(self, state):
        self.active = state
        if self.active:
            palette = self.palette()
            palette.setColor(self.backgroundRole(), self.active_color)
            self.setPalette(palette)
            if self.label is not None:
                self.label.setVisible(True)
                self.label.setStyleSheet("color: #000000;")
            self.icon_layout.itemAt(1).widget().setParent(None)
            self.icon_layout.insertWidget(1, self.icon_active)
        else:
            palette = self.palette()
            palette.setColor(self.backgroundRole(), self.background_color)
            self.setPalette(palette)
            self.icon_layout.itemAt(1).widget().setParent(None)
            self.icon_layout.insertWidget(1, self.icon_inactive)
            if self.label is not None:
                self.label.setVisible(False)
                self.label.setStyleSheet("QLabel {color: #ffffff;}")

    def enterEvent(self, event):
        if not self.active:
            self.icon_layout.itemAt(1).widget().setParent(None)
            self.icon_layout.insertWidget(1, self.icon_hover)
        if self.label is not None:
            self.label.setVisible(True)

    def leaveEvent(self, event):
        if not self.active:
            self.icon_layout.itemAt(1).widget().setParent(None)
            self.icon_layout.insertWidget(1, self.icon_inactive)
        if self.label is not None:
            self.label.setVisible(self.active)

    def mousePressEvent(self, event):
        self.paneSelected.emit(self)


class PaneSwitcher(QWidget):
    def __init__(self, translator):
        super(PaneSwitcher, self).__init__()
        self.translator = translator
        self.setMaximumHeight(100)
        self.active_pane = 0
        self.panes = []
        self.activities = PaneSelectItem(path.join("pixmaps", "activities_gray.svg"),
                                         path.join("pixmaps", "activities_black.svg"),
                                         path.join("pixmaps", "activities_white.svg"),
                                         self.translator['fitness_pane_title'])
        self.activities.paneSelected.connect(self.pane_selected)
        self.panes.append(self.activities)
        self.nutriweight = PaneSelectItem(path.join("pixmaps", "nutrients_weight_gray.svg"),
                                          path.join("pixmaps", "nutrients_weight_black.svg"),
                                          path.join("pixmaps", "nutrients_weight_white.svg"),
                                          self.translator['food_tracking_pane_title'])
        self.nutriweight.paneSelected.connect(self.pane_selected)
        self.panes.append(self.nutriweight)
        self.layout = QHBoxLayout()
        for pane in self.panes:
            self.layout.addWidget(pane)
        self.setLayout(self.layout)
        self.update_active_pane()

    def update_active_pane(self):
        for i, pane in enumerate(self.panes):
            self.panes[i].set_active(i == self.active_pane)

    def pane_selected(self, pane_widget):
        for i, pane in enumerate(self.panes):
            if pane_widget == pane:
                self.active_pane = i
        self.update_active_pane()
