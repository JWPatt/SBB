"""
A script for querying the SBB API and the OSRM machine for a given origin city and set of destinations.
First gets the SBB data, which corrects typos and also delivers the lat/lon data needed for the OSRM queries.

As of 6.10.2021, a full search for a new location takes roughly 6 minutes: 30 seconds for the SBB API requests and
another 5 minutes for the OSRM routing (on my local machine at least, but this gives a rough estimate).
"""

import io_func
import core_func
import os

mgdb_url = os.environ.get('MONGODB_URI', None)
mgdb_in = io_func.MongodbHandler(mgdb_url, "SBB_time_map")
# destinations = set(mgdb_in.get_endnode_set('endnodes_Zurich'))
destinations = ['Landquart']
mgdb_out = io_func.MongodbHandler(mgdb_url, "test_20211005_2")

origin_city = ['Davos']
origin_details_list = []
for city in origin_city:
    origin_details_list.append(city)

for origin_details in origin_details_list:

    mgdb_in.set_col(origin_details)
    mgdb_out.set_col(origin_details)

    sbb_results = core_func.sbb_api_asyncio_wrapper(origin_details, destinations)
    osrm_results = core_func.osrm_wrapper(origin_details, sbb_results)
    final_results = core_func.add_hovertext_difference(osrm_results)

    mgdb_out.write_data_dict_of_dict(final_results)
