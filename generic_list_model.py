#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from PyQt5.QtCore import Qt, QAbstractListModel


class GenericListModel(QAbstractListModel):
    def __init__(self, *args):
        super(GenericListModel, self).__init__(*args)
        self.list = []

    def __iter__(self):
        return iter(self.list)

    def rowCount(self, parent=None, *args, **kwargs):
        if parent:
            return len(self.list)

    def data(self, index, role=None):
        return self.list[index.row()]

    def data_by_int_index(self, index):
        return self.list[index]

    def append(self, item):
        item.data_changed.connect(self.data_changed)
        self.list.append(item)
        new_index = self.createIndex(len(self.list), 0, item)
        self.dataChanged.emit(new_index, new_index, [Qt.EditRole])

    def pop(self, index):
        self.list.pop(index)
        i = min(index, len(self.list) - 1)
        new_index = self.createIndex(i, 0, self.list[i])
        self.dataChanged.emit(new_index, new_index, [Qt.EditRole])

    def data_changed(self, item):
        model_index = self.createIndex(self.list.index(item), 0, item)
        self.setData(model_index, item)

    def setData(self, model_index, data, role=Qt.EditRole):
        super(GenericListModel, self).setData(model_index, data, role=role)
        self.dataChanged.emit(model_index, model_index, [role])

    def reset_whole_list(self):
        for item in self.list:
            item.reset()

    def clear(self):
        self.list = []

    def is_empty(self):
        return len(self.list) <= 0
