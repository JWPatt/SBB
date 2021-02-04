import pandas as pd

def betriebspunkt_to_dict(all_city_file_name):
    names = pd.read_csv(all_city_file_name, sep=',',header=0, encoding="ISO-8859-1")['Name'].to_dict()
    return names

def read_intermediate_data(intermediate_data_name):
    data_segment = {}
    df = pd.read_csv(intermediate_data_name, header=None,index_col=0).reset_index().to_dict(orient='list')
    for i in range(0,len(df[0])):
        data_segment[df[0][i]] = [df[1][i], df[2][i], df[3][i]]
    return data_segment

def read_list_of_cities(cities_file_name):
    data_portion = set(pd.read_csv(cities_file_name, header=None, encoding="ISO-8859-1")[0])
    data_portion = {key: None for key in data_portion}
    return data_portion