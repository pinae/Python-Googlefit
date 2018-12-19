#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import pyqtSignal, QUrl
from urllib.parse import parse_qs


class Browser(QWebEngineView):
    approvalCode_received = pyqtSignal(str)
    titleChanged = pyqtSignal(str)

    def __init__(self):
        self.view = QWebEngineView.__init__(self)
        self.setGeometry(0, 0, 800, 1000)
        self.titleChanged.connect(self.adjust_title)
        self.loadFinished.connect(self.page_loaded)

    def load(self, url):
        self.setUrl(QUrl(url))

    def adjust_title(self):
        self.titleChanged.emit(self.title())

    def page_loaded(self):
        url = self.url().toString()
        if url.startswith("https://accounts.google.com/o/oauth2/approval/v2"):
            self.approvalCode_received.emit(parse_qs(url)['approvalCode'][0])
