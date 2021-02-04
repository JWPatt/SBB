# take a dict of  city:[lat,lon,duration] and write to file
# for when the info is already known and checked and not needed to be re-looked up
def write_data_portion(data_portion, openfile):
    for key in data_portion:
        openfile.write('"' + key + '",' + str(data_portion[key][0]) + ',' + str(data_portion[key][1]) + ',' + str(data_portion[key][2]))
        openfile.write('\n')


# take in the [lat,lon,duration] and city name and write to file
# for when the info is already known and not needed to be re-looked up
def write_data_line(destination, data_list, openfile):
    # csv_writer = writer(openfile)
    # csv_writer.writerow(openfile,[destination, str(data_list[0]), str(data_list[1]), str(data_list[2])])
    openfile.write('"' + destination + '",' + str(data_list[0]) + ',' + str(data_list[1]) + ',' + str(data_list[2]))
    openfile.write('\n')

# take in the city name and write to file
def write_destination_line(destination, openfile):
    # csv_writer = writer(openfile)
    # csv_writer.writerow(openfile,[destination, str(data_list[0]), str(data_list[1]), str(data_list[2])])
    openfile.write('"' + destination + '"' )
    openfile.write('\n')


def write_line_to_shit_list(destination, shitlist_name):
    shitlist = open_shitlist(shitlist_name)
    shitlist[destination] = None
    with open(shitlist_name, 'w', newline='') as shitlist_file:
        for key in shitlist.keys():
            shitlist_file.write('"' + str(key) + '"')
            shitlist_file.write('\n')


def open_shitlist(shitlist_name):
    import pandas as pd
    import os
    shitlist = {}
    if os.path.isfile(shitlist_name):
        df = pd.read_csv(shitlist_name, header=None)
        for i in df[0]:
            shitlist[i] = None
    return shitlist


def write_old_intermediate_data(data, openfile):
    for key in data:
        openfile.write('"' + key + '",' + str(data[key][0]) + ',' + str(data[key][1]) + ',' + str(data[key][2]))
        openfile.write('\n')
    openfile.flush()
