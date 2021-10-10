import os
import sys
import core_func
import asyncio


def sbb_api_asyncio_wrapper(origin_details, data_set_master):
    """Queries the SBB API asynchronously, processes results, and returns them

    Args:
        origin_details (str): origin city
        data_set_master (set): set of destination cities

    Returns:
        dict of dict: full processed results with SBB time table information
    """
    try:
        dest_per_query = 200

        return asyncio.run(core_func.sbb_api_asyncio.async_api_handler(origin_details, data_set_master, dest_per_query))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, e)
        raise
