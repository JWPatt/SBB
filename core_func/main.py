import multiprocessing as mp
import time
import os
import sys
import io_func
import core_func
from core_func.sbb_api import sbb_query_and_update
from core_func.sbb_api_2 import sbb_query_and_update_2
from pprint import pprint
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def primary(origin_details, mgdb):

    if mp.cpu_count() < 2:
        print('Function not set up for less than 2 threads! Terminating.')
        return 0

    try:
        # Load file names
        dir_prefix = ''
        if __name__ == '__main__':
            dir_prefix = '../'

        main_table_csv = dir_prefix + io_func.database_loc('output_csvs/', origin_details)
        all_city_file_csv = dir_prefix + 'input_csvs/Betriebspunkt_short.csv'
        key_cities_csv = dir_prefix + 'input_csvs/key_cities_sbb_short.csv'
        bad_destinations_csv = dir_prefix + 'output_csvs/shitlist.csv'
        misspelled_destinations_csv = dir_prefix + 'output_csvs/typos.csv'
        extrema_destinations_csv = dir_prefix + 'output_csvs/extrema.csv'
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
        nthreads = 3
        pool = mp.Pool(nthreads)

        # Begin http session
        session = requests.Session()
        retry = Retry(connect=1, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)


        duration_counter = 0
        data = manager.dict()
        # data = {}
        old_data = {}
        bad_destinations = set()
        misspelled_destinations = set()
        extrema_destinations = set()
        not_extrema_destinations = set()
        output_sets = [bad_destinations, misspelled_destinations, extrema_destinations, not_extrema_destinations]

        old_data.update(io_func.csv_to_dict(main_table_csv))
        print("Loading previous data of {old_data} cities.".format(old_data=str(len(old_data))))
        data.update(io_func.betriebspunkt_csv_to_empty_dict(all_city_file_csv))
        data.update(io_func.csv_to_empty_dict(key_cities_csv))
        data.update(old_data)
        data=(mgdb.get_endnode_set('endnodes_Zurich'))

        bad_destinations.update(io_func.csv_to_set(bad_destinations_csv))
        misspelled_destinations.update(io_func.csv_to_set(misspelled_destinations_csv))
        extrema_destinations.update(io_func.csv_to_set(extrema_destinations_csv))

        n_extrema = len(extrema_destinations)
        n_misspelled = len(misspelled_destinations)
        n_bad = len(bad_destinations)

        jobs = []

        known_destinations = mgdb.get_destination_set(origin_details)
        pop_counter = 0
        for destination in set(data):
            if destination in known_destinations:
                data.discard(destination)
                pop_counter += 1
        print('discarded ', pop_counter, " destinations, out of ", (len(data)+pop_counter))
        print('leftover ', data)

        t_init = time.time()
        dest_per_query = 220
        # data_list_master = list(data)
        data_set_master = set(data)
        data_list_of_lists = [list(data_set_master)[x:x+dest_per_query] for x in range(0,len(data_set_master),dest_per_query)]

        # listener = pool.apply_async(core_func.listen_and_spawn_job, (data_list_master, origin_details, q))

        for i in range(nthreads):
            if len(data_set_master) > 0:
                data_list = list(data_set_master)[0:dest_per_query]
                data_set_master.difference_update(set(data_list))
                job = pool.apply_async(sbb_query_and_update_2, (data_list, q, origin_details,session))
                jobs.append(job)

        results = {}
        index = 0
        for job in jobs:
            index += 1
            data_portion, td_get = job.get()
            core_func.update_dict_min_duration(results, data_portion)
            data_set_master.difference_update(data_portion.keys())
            print ('(',len(data_set_master),' destinations remaining)')
            try:
                if len(data_list) > 0:
                    data_list = list(data_set_master)[0:dest_per_query]
                    data_set_master.difference_update(set(data_list))
                    job = pool.apply_async(sbb_query_and_update_2, (data_list, q, origin_details,session))
                    jobs.append(job)
            except IndexError:
                print('no more jobs to add')



        pool.close()
        pool.join()
        t_init = time.time()
        mgdb.write_data_dict_of_dict(results)
        print('Time to clear the stack: ' + str(time.time() - t_init) + ' seconds, and ' + str(index) + 'API queries')


        io_func.write_destination_set_to_csv(bad_destinations, bad_destinations_csv)
        io_func.write_destination_set_to_csv(misspelled_destinations, misspelled_destinations_csv)
        io_func.write_destination_set_to_csv(extrema_destinations, extrema_destinations_csv)
        print("Added %s, %s, and %s to bad, misspelled, and extrema desntination csvs." % (
            (len(bad_destinations) - n_bad),
            (len(misspelled_destinations) - n_misspelled),
            (len(extrema_destinations) - n_extrema)))

    except KeyboardInterrupt or EOFError:
        print("Killing process: writing extrema, misspelled, and bad destination csv's first.")
        if extrema_destinations:
            print("End node destination list: added " + str(len(extrema_destinations) - n_extrema) + " destinations to list.")
            io_func.write_destination_set_to_csv(extrema_destinations, extrema_destinations_csv)
        if misspelled_destinations:
            print("Misspelled destination list: added " + str(len(misspelled_destinations) - n_misspelled) + " destinations to list.")
            io_func.write_destination_set_to_csv(misspelled_destinations, misspelled_destinations_csv)
        if bad_destinations:
            print("Bad destination list: added " + str(len(bad_destinations) - n_bad) + " destinations to list.")
            io_func.write_destination_set_to_csv(bad_destinations, bad_destinations_csv)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno, e)
        raise

    return 1


if __name__ =="__main__":
    origin_details = ['Bern', '2021-06-26', '7:01']
    mgdb = io_func.MongodbHandler("127.0.0.1:27017", "SBB_time_map")
    mgdb.set_col(['Bern', '2021-06-26', '7:01'])

    t_init = time.time()
    primary(origin_details, mgdb)
    print(time.time() - t_init)