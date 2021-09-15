import multiprocessing as mp
import time
import os
import sys
import io_func
import core_func
from core_func.sbb_api_alternative import sbb_query_and_update
from core_func.sbb_api_2_class import sbb_api_manager
from core_func.sbb_api_asyncio import async_query_and_process
from pprint import pprint
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import aiohttp
import asyncio


def primary_wrapper(origin_details, mgdb):

    if mp.cpu_count() < 2:
        print('Function not set up for less than 2 threads! Terminating.')
        return 0

    try:
        # Load input file names
        dir_prefix = ''
        if __name__ == '__main__':
            dir_prefix = '../'

        # Initialize various
        endnodes = (mgdb.get_endnode_set('endnodes_Zurich'))
        data_set_master = set(endnodes)

        # Remove destinations where we already have data
        known_destinations = mgdb.get_destination_set(origin_details)
        pop_counter = 0
        for destination in set(endnodes):
            if destination in known_destinations:
                data_set_master.discard(destination)
                pop_counter += 1
        print('discarded ', pop_counter, " destinations, out of ", (len(data_set_master) + pop_counter))
        # if pop_counter >= 2750:
            # return 1

        # t_init = time.time()
        dest_per_query = 200

        results = asyncio.run(core_func.sbb_api_asyncio.async_api_handler(origin_details, data_set_master, dest_per_query))
        print(results)
    # except KeyboardInterrupt or EOFError:
    #     mgdb.write_data_dict_of_dict(results)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno, e)
        raise

    return 1


if __name__ == "__main__":

    mgdb = io_func.MongodbHandler(pd.read_csv("../io_func/secret_mgdb_pw.csv"), "SBB_time_map")

    origin_city = ['Locarno']
    origin_date = ['2021-06-25']
    origin_time = ['7:01']
    origin_details_list = []
    for city in origin_city:
        for date in origin_date:
            for time in origin_time:
                origin_details_list.append([city, date, time])

    for origin_details in origin_details_list:
        print(origin_details)
        mgdb.set_col(origin_details)
        success = core_func.primary_wrapper(origin_details, mgdb)
