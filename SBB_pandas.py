import multiprocessing as mp
import time
import os
import sys
import pandas
import io_func
from sbb_api import sbb_query_and_update
from html_plot import make_html_map


def main(origin_details):

    if mp.cpu_count() < 2:
        print('Function not set up for less than 2 threads! Terminating.')
        return 0

    try:
        # Load file names
        key_cities_csv = 'input_csvs/key_cities_sbb_short.csv'
        all_city_file_csv = 'input_csvs/Betriebspunkt_short.csv'
        # main_table_csv = 'output_csvs/Zurich_HB_7:00_2021-06-25.csv'
        main_table_csv = io_func.database_loc(origin_details)
        bad_destinations_csv = 'output_csvs/shitlist.csv'
        extrema_destinations_csv = 'output_csvs/extrema.csv'
        misspelled_destinations_csv = 'output_csvs/typos.csv'
        fresh_start = False

        if fresh_start:
            if os.path.isfile(main_table_csv):
                os.system("rm " + main_table_csv)
                os.system("touch " + main_table_csv)
            if os.path.isfile(bad_destinations_csv):
                os.system("rm " + bad_destinations_csv)
                os.system("touch " + bad_destinations_csv)
            if os.path.isfile(extrema_destinations_csv):
                os.system("rm " + extrema_destinations_csv)
                os.system("touch " + extrema_destinations_csv)
            if os.path.isfile(misspelled_destinations_csv):
                os.system("rm " + misspelled_destinations_csv)
                os.system("touch " + misspelled_destinations_csv)

        # Load parallel processing tools
        manager = mp.Manager()
        q = manager.Queue()
        pool = mp.Pool(2)

        duration_counter = 0
        data = manager.dict()
        old_data = {}
        bad_destinations = set()
        misspelled_destinations = set()
        extrema_destinations = set()
        not_extrema_destinations = set()

        # if os.path.isfile(main_table + '') is False:
        data.update(io_func.betriebspunkt_csv_to_empty_dict(all_city_file_csv))
        data.update(io_func.csv_to_empty_dict(key_cities_csv))
        extrema_destinations.update(io_func.csv_to_set(extrema_destinations_csv))
        misspelled_destinations.update(io_func.csv_to_set(misspelled_destinations_csv))

        if origin_details[0] in data:
            del data[origin_details[0]]
        if os.path.isfile(main_table_csv) is True:
            try:
                old_data = io_func.csv_to_dict(main_table_csv)
                print("Adding old_data of {old_data} cities into data, which has {data} cities".format(
                    old_data=str(len(old_data)), data=str(len(data))))
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
        print("Done loading input and old data.")

        n_extrema = len(extrema_destinations)
        n_misspelled = len(misspelled_destinations)
        n_bad = len(bad_destinations)

        jobs = []
        stack_counter = 0
        t_init = time.time()
        listener = pool.apply_async(listen_and_write, (main_table_csv, data, duration_counter, old_data, q,))

        for key in sorted(list(data), key=lambda x: 1):
            if key in bad_destinations or key in misspelled_destinations:
                continue
            if data[key] is None:
                extrema_destinations.add(key)
                stack_counter += 1
                print('Adding ' + key + ' to Pool.')
                job = pool.apply_async(sbb_query_and_update, (key, data, q, origin_details))
                jobs.append(job)
                if stack_counter == 50000:
                    break
        print('%d cities have been loaded onto the stack.' % stack_counter)
        print('Time to load stack: %d seconds' % (time.time()-t_init))

        # collect results from the workers through the pool result queue
        t_init = time.time()
        for job in jobs:
            try:
                destination, data_portion, td_get = job.get()
                # print(destination, data_portion)
                if not data_portion:  # if it doesn't exist, it goes to bad_destinations
                    bad_destinations.add(destination)
                    extrema_destinations.discard(destination)
                else:
                    for key in list(data_portion):
                        if data_portion[key] is None:
                            not_extrema_destinations.add(key)
                            if key != destination:
                                misspelled_destinations.add(key)  # the city name given is not the city name returned; is therefore a typo
                                if destination not in not_extrema_destinations:
                                    extrema_destinations.add(destination)
                            del data_portion[key]
                        if key in extrema_destinations:
                            if destination != key:
                                extrema_destinations.discard(key)  # if this key is not the final destination, it cannot be an extrema
                    if data_portion:
                        q.put((data_portion, td_get))
            except EOFError:
                print("Ran out of free API requests")
                break
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno, e)
                raise

        print ('Time to clear the stack: ' + str(time.time()-t_init) + ' seconds')

        # now we are done, kill the listener
        q.put('kill')
        pool.close()
        pool.join()

        print( "End node destination list: added " + str(len(extrema_destinations) - n_extrema) + " destinations to list.")
        io_func.write_destination_set_to_csv(extrema_destinations, extrema_destinations_csv)
        print("Misspelled destination list: added " + str(len(extrema_destinations) - n_extrema) + " destinations to list.")
        io_func.write_destination_set_to_csv(misspelled_destinations, misspelled_destinations_csv)
        print("Bad destination list: added " + str(len(extrema_destinations) - n_extrema) + " destinations to list.")
        io_func.write_destination_set_to_csv(bad_destinations, bad_destinations_csv)

    except KeyboardInterrupt or EOFError:
        print("Killing process: writing extrema, misspelled, and bad destination csv's first.")
        if extrema_destinations:
            print("End node destination list: added " + str(len(extrema_destinations) - n_extrema) + " destinations to list.")
            io_func.write_destination_set_to_csv(extrema_destinations, extrema_destinations_csv)
        if misspelled_destinations:
            print("Misspelled destination list: added " + str(len(extrema_destinations) - n_extrema) + " destinations to list.")
            io_func.write_destination_set_to_csv(misspelled_destinations, misspelled_destinations_csv)
        if bad_destinations:
            print("Bad destination list: added " + str(len(extrema_destinations) - n_extrema) + " destinations to list.")
            io_func.write_destination_set_to_csv(bad_destinations, bad_destinations_csv)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        raise

    return 1



def listen_and_write(main_table_csv, data, duration_counter, old_data, q):
    '''listens for messages on the q, writes to open file. '''
    with open(main_table_csv, 'w', encoding='utf-8') as openfile:
        for key in old_data:
            io_func.write_data_line_to_open_csv(key, old_data[key], openfile)
            openfile.flush()

        while 1:
            try:
                (data_portion, td_get) = q.get()
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
                print('{:<30} | {:>3} new durations  | {:>6} total durations  |  {:>3}'.format(key,chain_counter,duration_counter,td_get))
            except EOFError:
                print("Ran out of free API requests")
                return
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                # print(exc_type, fname, exc_tb.tb_lineno, e)
                raise


if __name__ == "__main__":

    # Enter city name with or without special characters (probably safer without)
    # Enter time in HH:MM format (e.g. '13:10')
    # Enter date in YYYY-MM-DD format (e.g. '2021-11-22')
    origin_city = ['Zurich HB', 'Bern', 'Geneva']
    origin_time = ['7:00','7:00','7:00']
    origin_date = ['2021-06-25','2021-06-25','2021-06-25']
    origin_details = [[origin_city[i], origin_time[i], origin_date[i]] for i in range(3)]
    try:
        for i in origin_details[:1]:
            success = main(i)
            if success:
                data_csv = io_func.database_loc(i)
                make_html_map(data_csv, i)
    except KeyboardInterrupt or EOFError:
        print("Killed by user.")
