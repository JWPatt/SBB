import multiprocessing as mp
import time
import os
import pandas
import io_func
from sbb_api import sbb_query_and_update


def main():
    key_cities_csv = 'input_csvs/key_cities_sbb.csv'
    all_city_file_csv = 'input_csvs/Betriebspunkt_short.csv'
    main_table_csv = 'output_csvs/main_table.csv'
    bad_destinations_csv = 'output_csvs/shitlist.csv'
    extrema_csv = 'output_csvs/extrema.csv'
    typos_csv = 'output_csvs/typos.csv'
    fresh_start = False

    if fresh_start:
        if os.path.isfile(main_table_csv):
            os.system("rm " + main_table_csv)
            os.system("touch " + main_table_csv)
        if os.path.isfile(bad_destinations_csv):
            os.system("rm " + bad_destinations_csv)
            os.system("touch " + bad_destinations_csv)
        if os.path.isfile(extrema_csv):
            os.system("rm " + extrema_csv)
            os.system("touch " + extrema_csv)
        if os.path.isfile(typos_csv):
            os.system("rm " + typos_csv)
            os.system("touch " + typos_csv)



    # must use Manager queue here, or will not work
    manager = mp.Manager()
    q = manager.Queue()
    # pool = mp.Pool(mp.cpu_count())
    print("Number of cores: " + str(mp.cpu_count()))
    pool = mp.Pool(2)

    API_counter = 0
    duration_counter = 0
    data = manager.dict()
    old_data = {}
    bad_destinations = set()
    typos = set()
    extrema = set()
    not_extrema = set()

    # if os.path.isfile(main_table + '') is False:
    data.update(io_func.betriebspunkt_csv_to_empty_dict(all_city_file_csv))
    data.update(io_func.csv_to_empty_dict(key_cities_csv))
    extrema.update(io_func.csv_to_set(extrema_csv))
    typos.update(io_func.csv_to_set(typos_csv))


    if 'Zürich HB' in data: del data['Zürich HB']
    if os.path.isfile(main_table_csv) is True:
        try:
            old_data = io_func.csv_to_dict(main_table_csv)
            print("Adding old_data of " + str(len(old_data)) + " cities into data, which has " + str(len(data)) + " cities - ok?")
            data.update(old_data)
            bad_destinations = io_func.csv_to_set(bad_destinations_csv)
        except pandas.errors.EmptyDataError:
            if os.path.isfile(main_table_csv): os.remove(main_table_csv)
            if os.path.isfile(bad_destinations_csv): os.remove(bad_destinations_csv)
            data.update(io_func.betriebspunkt_csv_to_empty_dict(all_city_file_csv))
            data.update(io_func.csv_to_empty_dict(key_cities_csv))
            if 'Zürich HB' in data: del data['Zürich HB']
    else:
        os.system("touch " + main_table_csv)

    jobs = []
    stack_counter = 0
    t_init = time.time()
    listener = pool.apply_async(listen_and_write, (main_table_csv, data, duration_counter, old_data, q,))

    for key in sorted(list(data), key=lambda x: 1):
        if key in bad_destinations or key in typos:
            continue
        if data[key] is None:
            extrema.add(key)
            stack_counter += 1
            print('Adding ' + key + ' to Pool.')
            job = pool.apply_async(sbb_query_and_update, (key, data, q))
            jobs.append(job)
            if stack_counter == 500000:
                break
    print(str(stack_counter) + ' cities have been loaded onto the stack.')
    print('Time to load stack: ' + str(time.time()-t_init) + ' seconds')

    # collect results from the workers through the pool result queue
    t_init = time.time()
    for job in jobs:
        destination, data_portion = job.get()
        print(destination, data_portion)
        if not data_portion:  # if it doesn't exist, it goes to bad_destinations
            bad_destinations.add(destination)
            extrema.discard(destination)
        else:
            for key in list(data_portion):
                if data_portion[key] is None:
                    not_extrema.add(key)
                    if key != destination:
                        typos.add(key)  # the city name given is not the city name returned; is therefore a typo
                        if destination not in not_extrema:
                            extrema.add(destination)
                    del data_portion[key]
                if key in extrema:
                    if destination != key:
                        extrema.discard(key)  # if this key is not the final destination, it cannot be an extrema
            if data_portion:
                q.put(data_portion)
    print ('Time to clear the stack: ' + str(time.time()-t_init) + ' seconds')

    # now we are done, kill the listener
    q.put('kill')
    pool.close()
    pool.join()

    io_func.write_destination_set_to_csv(extrema, extrema_csv)
    io_func.write_destination_set_to_csv(typos, typos_csv)
    io_func.write_destination_set_to_csv(bad_destinations, bad_destinations_csv)


def listen_and_write(main_table_csv, data, duration_counter, old_data, q):
    '''listens for messages on the q, writes to open file. '''
    with open(main_table_csv, 'w') as openfile:
        # csv_writer = writer(openfile)
        for key in old_data:
            io_func.write_data_line_to_open_csv(key, old_data[key], openfile)
            openfile.flush()

        while 1:
            data_portion = q.get()
            chain_counter = 0
            for key in list(data_portion):
                if key not in data:
                    data[key] = data_portion[key]
                    io_func.write_data_line_to_open_csv(key, data[key], openfile)
                    openfile.flush()
                    chain_counter += 1
                elif data[key] is None:
                    data[key] = data_portion[key]
                    io_func.write_data_line_to_open_csv(key, data[key], openfile)
                    openfile.flush()
                    chain_counter += 1
            duration_counter += chain_counter
            print('API for ' + key + ' yielded ' + str(chain_counter) + ' new durations, for a total of ' + str(duration_counter))


if __name__ == "__main__":
    main()
