import pandas as pd

def csv_to_set(file_name):
    names = pd.read_csv(file_name, sep=',',header=0, encoding="ISO-8859-1")['Name'].to_set()
    return names

def betriebspunkt_to_dict(all_city_file_name):
    names = pd.read_csv(all_city_file_name, sep=',',header=0, encoding="ISO-8859-1")['Name'].to_dict()
    return names

def read_intermediate_data(intermediate_data_name):
    data_segment = {}
    df = pd.read_csv(intermediate_data_name, header=None,index_col=0).reset_index().to_dict(orient='list')
    for i in range(0,len(df[0])):
        data_segment[df[0][i]] = [df[1][i], df[2][i], df[3][i]]
    return data_segment