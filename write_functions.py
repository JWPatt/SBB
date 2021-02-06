from read_in_csv import csv_to_empty_dict


# take in the destination and [lat,lon,duration] name and write line to an already open file
def write_data_line(destination, data_list, openfile):
    openfile.write('"' + destination + '",' + str(data_list[0]) + ',' + str(data_list[1]) + ',' + str(data_list[2]) +
                   '\n')


# take in a dict of {destination: [lat,lon,duration]} and write all lines to an already open file
def write_data_to_csv(data, openfile):
    for destination in data:
        write_data_line(destination)
    openfile.flush()


# take in the destination name and write to an open file
# used for recording the extrema and typos after processing, where the full set of destinations is known
def write_destination_to_csv(destination, openfile):
    openfile.write('"' + destination + '"' + '\n')
