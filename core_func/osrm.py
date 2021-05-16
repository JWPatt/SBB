import multiprocessing as mp
import time
import os
import sys
import io_func
import core_func
from core_func.sbb_api_alternative import sbb_query_and_update
from core_func.sbb_api_2 import sbb_query_and_update_2
from pprint import pprint
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from difflib import get_close_matches
from io_func.mongodb_crud import write_osrm_line_to_mongodb

def osrm_query(origin_city, dest_cities, city_latlon_table, osrm_url, req_session):
    t_init = time.time()
    # for dest_city in dest_cities:
    count = 0
    return_dict = {}
    for dest_city in dest_cities:
        count += 1
        origin_latlon = city_latlon_table[origin_city]
        dest_latlon = city_latlon_table[dest_city]
        query_url = osrm_url + '/route/v1/driving/' + str(origin_latlon['lon']) + ',' + str(origin_latlon['lat']) +';'
        query_url = query_url + str(dest_latlon['lon']) + ',' + str(dest_latlon['lat']) + '?steps=false'
        print(query_url)

        response = req_session.get(query_url)
        jdata = response.json()
        return_dict[dest_city] = {}
        if response.status_code == 200:
            print(count)
            return_dict[dest_city]['travel_time'] = jdata['routes'][0]['duration']
            return_dict[dest_city]['destination'] = dest_city
            return_dict[dest_city]['lat'] = city_latlon_table[dest_city]['lat']
            return_dict[dest_city]['lon'] = city_latlon_table[dest_city]['lon']
        if count > 10: break

    return return_dict



if __name__ == "__main__":
    # list_of_locations = {
    #     "Zurich HB": {"lat": 47.3779, "lon": 8.5403},
    #     "Bern": {"lat": 46.9490, "lon": 7.4385},
    #     "Geneva": {"lat": 46.2044, "lon": 6.1413},
    #     "Lugano": {"lat": 46.0037, "lon": 8.9511},
    #     "Basel": {"lat": 47.5596, "lon": 7.5886},
    #     "Lausanne": {"lat": 46.5197, "lon": 6.6323},
    #     "Sion": {"lat": 46.2331, "lon": 7.3606},
    # }

    session = requests.Session()
    url = pd.read_csv("../io_func/secret_mgdb_pw.csv")
    mgdb = io_func.MongodbHandler(url, "SBB_time_map")
    locations = mgdb.get_endnode_dict('Zurich_HB.2021_06_26.7_00')
    list_of_locations = list(locations.keys())

    # start = 'Lugano'
    # start = get_close_matches(start,list_of_locations)[0]
    # print(start)

    # list_of_locations = ['Lugano','Bern']

    locations = osrm_query('Lugano, Autosilo Balestra', list_of_locations, locations, 'http://127.0.0.1:5000', session)
    # print(locations)
    df = pd.DataFrame.from_dict(locations, orient='index')
    # df = pd.DataFrame(list_of_locations)
    # df.to_csv('osrm.csv')
    print(df)
    # for key in locations:
        # write_osrm_line_to_mongodb(url, "SBB_time_map", "Zurich", locations[key])

