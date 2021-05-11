import multiprocessing as mp
import time
import os
import sys
import io_func
import core_func
from core_func.sbb_api import sbb_query_and_update
from core_func.sbb_api_2 import sbb_query_and_update_2
from core_func.sbb_api_2_class import sbb_api_manager
from pprint import pprint
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def primary(origin_details, mgdb):

    if mp.cpu_count() < 2:
        print('Function not set up for less than 2 threads! Terminating.')
        return 0

    try:
        # Load input file names
        dir_prefix = ''
        if __name__ == '__main__':
            dir_prefix = '../'
        all_city_file_csv = dir_prefix + 'input_csvs/Betriebspunkt_short.csv'
        key_cities_csv = dir_prefix + 'input_csvs/key_cities_sbb_short.csv'

        # Load parallel processing tools
        manager = mp.Manager()
        q = manager.Queue()
        nthreads = 3
        pool = mp.Pool(nthreads)

        # Begin http session
        session = requests.Session()
        retry = Retry(connect=1, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)

        # Create sbb api class
        sbb_api_2 = sbb_api_manager(session)

        # Initialize various
        endnodes = (mgdb.get_endnode_set('endnodes_Zurich'))
        endnodes = io_func.csv_to_set("../input_csvs/endnodes_Zurich.csv")
        data_set_master = set(endnodes)

        # Remove destinations where we already have data
        known_destinations = mgdb.get_destination_set(origin_details)
        pop_counter = 0
        for destination in set(endnodes):
            if destination in known_destinations:
                data_set_master.discard(destination)
                pop_counter += 1
        print('discarded ', pop_counter, " destinations, out of ", (len(data_set_master)+pop_counter))
        if pop_counter >= 2750:
            return 1

        t_init = time.time()
        dest_per_query = 210

        jobs = []
        for i in range(nthreads):
            if len(data_set_master) > 0:
                data_list = list(data_set_master)[0:dest_per_query]
                data_set_master.difference_update(set(data_list))
                job = pool.apply_async(sbb_api_2.sbb_query_and_update_2, (data_list, q, origin_details))
                jobs.append(job)

        results = {}
        index = 0
        for job in jobs:
            index += 1
            data_portion, td_get = job.get()
            core_func.update_dict_min_duration(results, data_portion)
            data_set_master.difference_update(data_portion.keys())
            print('(',len(data_set_master),' destinations remaining)')
            try:
                if len(data_list) > 0:
                    data_list = list(data_set_master)[0:dest_per_query]
                    data_set_master.difference_update(set(data_list))
                    job = pool.apply_async(sbb_api_2.sbb_query_and_update_2, (data_list, q, origin_details))
                    jobs.append(job)
            except IndexError:
                print('no more jobs to add')
        pool.close()
        pool.join()

        while len(data_list) >= 1:
            data_list = list(data_set_master)[0:dest_per_query]
            data_set_master.difference_update(set(data_list))
            job = pool.apply_async(sbb_api_2.sbb_query_and_update_2, (data_list, q, origin_details))

        t_init = time.time()
        # mgdb.write_data_dict_of_dict(results)
        print('Time to clear the stack: ' + str(time.time() - t_init) + ' seconds, and ' + str(index) + 'API queries')




    # except KeyboardInterrupt or EOFError:
    #     mgdb.write_data_dict_of_dict(results)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno, e)
        raise

    return 1


if __name__ =="__main__":
    # origin_details = ['Zurich HB', '2021-06-26', '7:02']
    # pw = pd.read_csv("../io_func/secret_mgdb_pw.csv")
    # mgdb = io_func.MongodbHandler("mongodb+srv://admin_patty:"+pw.columns.to_list()[0]+"@cluster0.erwru.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", "SBB_time_map")
    # mgdb.set_col(['Zurich HB', '2021-06-26', '7:00'])
    #
    # t_init = time.time()
    # primary(origin_details, mgdb)
    # print(time.time() - t_init)

    # pw = pd.read_csv("../io_func/secret_mgdb_pw.csv")
    # mgdb = io_func.MongodbHandler("mongodb+srv://admin_patty:" + pw.columns.to_list()[
    #     0] + "@clusteruetliberg.erwru.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", "SBB_time_map")

    mgdb = io_func.MongodbHandler(pd.read_csv("../io_func/secret_mgdb_pw.csv"), "SBB_time_map")

    origin_city = ['Locarno']
    # origin_date = ['2021-06-25']
    # origin_time = ['6:00']
    # origin_city = ['Zurich HB', 'Bern', 'Geneva', 'Lugano', 'Basel', 'Lausanne']
    origin_date = ['2021-06-25' ]
    origin_time = ['7:00']
    origin_details_list = []
    for city in origin_city:
        for date in origin_date:
            for time in origin_time:
                origin_details_list.append([city, date, time])

    for origin_details in origin_details_list:
        print(origin_details)
        mgdb.set_col(origin_details)
        success = core_func.primary(origin_details, mgdb)
