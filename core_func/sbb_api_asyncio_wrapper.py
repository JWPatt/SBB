import os
import sys
import io_func
import core_func
import pandas as pd
import asyncio


def primary_wrapper(origin_details, mgdb):
    try:
        # Initialize variables
        data_set_master = set(mgdb.get_endnode_set('endnodes_Zurich'))
        dest_per_query = 200

        # Remove destinations where we already have data
        known_destinations = mgdb.get_destination_set(origin_details)
        for destination in set(data_set_master):
            if destination in known_destinations:
                data_set_master.discard(destination)

        results = asyncio.run(core_func.sbb_api_asyncio.async_api_handler(origin_details, data_set_master, dest_per_query))
        print(results)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
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
        success = core_func.primary_wrapper(io_func.reformat_origin_details(origin_details), mgdb)
