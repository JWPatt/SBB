def read_all_city_csv():
    import pandas as pd
    df = pd.read_csv('Betriebspunkt.csv', sep=',', header=0, encoding="ISO-8859-1")
    names = {}
    for i in df['Name']:
        names[i] = None

    return names


def read_csv_to_set(file_name):
    import pandas as pd
    df = pd.read_csv(file_name, sep=',',header=0, encoding="ISO-8859-1")
    names = set()
    for i in df['Name']:
        names.add(i)

    return names


def read_all_city_csv_short(all_city_file_name):
    import pandas as pd
    df = pd.read_csv(all_city_file_name, sep=',',header=0, encoding="ISO-8859-1")
    names = {}
    for i in df['Name']:
        names[i] = None

    return names


def read_intermediate_data(intermediate_data_name):
    import pandas as pd
    names = {}
    df = pd.read_csv(intermediate_data_name, header=None)
    # print(df)
    # print(df[0])
    # print(len(df[0]))
    for i in range(0,len(df[0])):
        names[df[0][i]] = [df[1][i], df[2][i], df[3][i]]

    return names




#
# data = read_all_city_csv()
# print(data)
# print(data.keys())
# print(data.values())