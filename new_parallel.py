import multiprocessing as mp
import time
from sbb_api_lookup_connection_multi import *
from read_in_csv import *
import os
import pandas
import random
from read_list_of_cities_csv import *

# a list of stations which will yield many between-stations, i.e. the extrema of the network

# a list of all stations in Switzerland, some 27,000.

# a csv containing stations, lat/log, and trip durations.
# during/after a run, data is stored here and then read by the plotting script
# if this script is rerun, the data in this csv will be loaded into the data dict and therefore
# no call to the SBB API is required, preventing unnecessary API calls

# written during the script, a list of names from which no data is given by the API
# the API is good at spelling errors, but sometimes the station just doesn't register or exist

# a list of cities which do not appear as intermediate cities in any search, i.e. a-priory unknown extrema

# deletes csv files and starts the program afresh (ie, clears cache)

key_cities_name = 'key_cities_sbb.csv'
all_city_file_name = 'Betriebspunkt_short.csv'
main_table = 'main_table.csv'
shitlist_name = 'shitlist.csv'
extrema_csv = 'extrema.csv'
typos_csv = 'typos.csv'
fresh_start = True

# os.system("rm " + main_table )
# input()
# os.system("rm " + main_table + " " + shitlist_name + " " + extrema_csv)

def main():

    if fresh_start:
        if os.path.isfile(main_table):
            os.system("rm " + main_table)
        if os.path.isfile(shitlist_name):
            os.system("rm " + shitlist_name)
        if os.path.isfile(extrema_csv):
            os.system("rm " + extrema_csv)
        if os.path.isfile(typos_csv):
            os.system("rm " + typos_csv)



    # must use Manager queue here, or will not work
    manager = mp.Manager()
    q = manager.Queue()
    # pool = mp.Pool(mp.cpu_count())
    print("Number of cores: " + str(mp.cpu_count()))
    pool = mp.Pool(3)

    API_counter = 0
    duration_counter = 0
    data = manager.dict()
    old_data = {}
    shitlist = {}
    typos = set()

    # if os.path.isfile(main_table + '') is False:
    data.update(betriebspunkt_to_dict(all_city_file_name))
    data.update(use_key_cities(key_cities_name))

    if 'Zürich HB' in data: del data['Zürich HB']
    if os.path.isfile(main_table) is True:
        try:
            old_data = read_intermediate_data(main_table)
            print("Adding old_data of " + str(len(old_data)) + " cities into data, which has " + str(len(data)) + " cities - ok?")
            data.update(old_data)
            shitlist = open_shitlist(shitlist_name)
        except pandas.errors.EmptyDataError:
            print('Starting simulation afresh - continue?')
            input()
            if os.path.isfile(main_table) is True: os.remove(main_table)
            if os.path.isfile(shitlist_name) is True: os.remove(shitlist_name)
            data.update(betriebspunkt_to_dict(all_city_file_name))
            data.update(use_key_cities(key_cities_name))
            if 'Zürich HB' in data: del data['Zürich HB']

    extrema = set(data.keys())
    not_extrema = set()

    # put listener to work first
    watcher = pool.apply_async(listener, (data, duration_counter,old_data, q,))

    #fire off workers
    jobs = []
    stack_counter = 0
    # for key in list(data):
    t_init = time.time()
    for key in sorted(list(data), key=lambda x: 1):
        if key in shitlist:
            continue
        if data[key] is None:
            stack_counter += 1
            print('Adding ' + key + ' to Pool.')
            job = pool.apply_async(update_master_table_multi, (key, data, q))  # TODO reorganize how parallelization works here
            jobs.append(job)
            if stack_counter == 500000:
                break
    print(str(stack_counter) + ' cities have been loaded onto the stack.')
    print('Time to load stack: ' + str(time.time()-t_init) + ' seconds')

    # collect results from the workers through the pool result queue
    t_init = time.time()
    for job in jobs:
        destination, data_portion = job.get()
        # data.update(data_portion)
        # print('got ' + str(destination) + ' and ' + str(data_portion))
        if not data_portion:  # if it doesn't exist, it goes to shitlist
            write_line_to_shit_list(destination, shitlist_name)  # TODO dont write directly, store and write at end
            # print('Writing ' + destination + ' to shitlist because data_portion is ' + str(data_portion))
            # del data[destination]
            extrema.discard(destination)
        else:
            for key in list(data_portion):  # do list() because dict cant change size during normal iteration
                if data_portion[key] is None:
                    not_extrema.add(key)
                    if key != destination:  # will only happen if it was a typo city
                        # write_line_to_shit_list(key, shitlist_name)
                        # print('Writing ' + key + ' to shitlist.')
                        typos.add(key)  # add the original typo'd name
                        # print('adding ' + destination + ' to typos')
                        if destination not in not_extrema:  # if it's not NOT an extrema, it could be an extrema
                            # print('adding ' + destination + ' to extrema')
                            extrema.add(destination)
                        # print ('removing ' + key + ' and ' + str(data_portion[key]))
                    del data_portion[key]
                    # else:
                    #     typos.add(destination)
                if key in extrema:
                    if destination != key:
                        extrema.discard(key)
            if data_portion:
                # print('listener is being fed ' + str(data_portion))
                q.put(data_portion)
            # else:
            #     if key in extrema:
            #         extrema.discard(key)
            #     extrema.add(destination)


    print ('Time to clear the stack: ' + str(time.time()-t_init) + ' seconds')

    #now we are done, kill the listener
    q.put('kill')
    pool.close()
    pool.join()

    with open(extrema_csv, 'w') as extremafile:
        print(str(extrema))
        for item in extrema:
            write_destination_line(item, extremafile)
            extremafile.flush()
    with open(typos_csv, 'w') as typosfile:
        for item in typos:
            write_destination_line(item, typosfile)
            typosfile.flush()


                ### 29.11.2020 fresh run: outputs empty file; rerun outputs many things
                ### 30.11.2020 still have the 29.11 problem, but now typo stations won't be shitlisted


def listener(data,duration_counter,old_data, q):
    '''listens for messages on the q, writes to file. '''
    # appends new results to the intermediate data file
    t_init = time.time()
    with open(main_table, 'w') as openfile:
        # csv_writer = writer(openfile)
        for key in old_data:
            write_data_line(key, old_data[key], openfile)
            openfile.flush()

        while 1:
            data_portion = q.get()
            # print('listener heard ' + str(data_portion))
            chain_counter = 0
            for key in list(data_portion):
                if key not in data:
                    data[key] = data_portion[key]
                    write_data_line(key, data[key], openfile)
                    openfile.flush()
                    # print("added new key to data: " + str(key))
                    chain_counter += 1
                elif data[key] is None:
                    data[key] = data_portion[key]
                    write_data_line(key, data[key], openfile)
                    openfile.flush()
                    # print("updated value in data: " + str(key))
                    chain_counter += 1
            duration_counter += chain_counter
            print('API for ' + key + ' yielded ' + str(chain_counter) + ' new durations, for a total of ' + str(duration_counter))

            # m = q.get()
            # if m == 'kill':
            #     f.write('killed')
            #     break
            # f.write(str(m) + '\n')
            # f.flush()


if __name__ == "__main__":
   main()