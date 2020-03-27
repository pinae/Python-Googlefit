# -*- coding: utf-8 -*-
from pandas import DataFrame


def save_weight_data(data):
    df = DataFrame(data, columns=["date", "weight"])
    df.to_csv("weight-data.csv")
