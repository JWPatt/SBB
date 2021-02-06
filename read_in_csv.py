import pandas as pd
import os


# The Betriebspunkt csv has a special format
def betriebspunkt_csv_to_empty_dict(file_name):
    data_portion = {}
    if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:
        data_portion = {key: None for key in (pd.read_csv(file_name, sep=',', encoding="ISO-8859-1")['Name'])}
    return data_portion


def csv_to_dict(file_name):
    data_portion = {}
    if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:
        df = pd.read_csv(file_name, header=None, index_col=0).reset_index().to_dict(orient='list')
        for i in range(0, len(df[0])):
            data_portion[df[0][i]] = [df[1][i], df[2][i], df[3][i]]
    return data_portion


def csv_to_empty_dict(file_name):
    data_portion = {}
    if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:
        data_portion = set(pd.read_csv(file_name, header=None, encoding="ISO-8859-1")[0])
        data_portion = {key: None for key in data_portion}
    return data_portion


def csv_to_set(file_name):
    data_portion = set()
    if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:
        data_portion = set(pd.read_csv(file_name, header=None, encoding="ISO-8859-1")[0])
    return data_portion
