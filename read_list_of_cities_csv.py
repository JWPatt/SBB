def read_list_of_cities(cities_file_name):

    import csv

    cities = {}
    with open(cities_file_name, 'r') as file:
        reader = csv.reader(file)
        # print (type(reader))
        for row in reader:
            for key in row:
                cities[key]=None

    return cities
