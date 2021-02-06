from read_in_csv import csv_to_empty_dict


# take in the destination and [lat,lon,duration] name and write line to an already open file
def write_data_line_to_open_csv(destination, data_list, openfile):
    openfile.write('"' + destination + '",' + str(data_list[0]) + ',' + str(data_list[1]) + ',' + str(data_list[2]) +
                   '\n')


# take in a dict of {destination: [lat,lon,duration]} and write all lines to an already open file
def write_data_to_open_csv(data, openfile):
    for destination in data:
        write_data_line_to_open_csv(destination)
    openfile.flush()


# take in the destination name and write to an open file
# used for recording the extrema and typos after processing, where the full set of destinations is known
def write_destination_to_csv(destination, openfile):
    openfile.write('"' + destination + '"' + '\n')


# take in a set of destination names and write to a file
# used at the end of processing, to update extrema/shitlist/typos csv's
def write_destination_set_to_csv(destination_set, file_name):
    with open(file_name, 'w') as file:
        print(str(destination_set))
        for destination in destination_set:
            write_destination_to_csv(destination, file)

