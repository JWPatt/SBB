import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pprint import pprint
import datetime
import core_func
import multiprocessing as mp
import aiohttp
import asyncio


# I just discovered a different API when allows for multiple destination searching - up to ~200 at a time!
# Total game changer, totally reshapes how the API queries will be structured. Eliminates the need for the
# parallelization, nearly.

# Since I need to rewrite this, I will add features that I determined would be useful while working on this app.
# old features: destination, lat, long, duration
# new features:
#   arrival time [int] - let the map be made by arrival time or travel duration
#   num transfers [int] - as above, mutatis mutandis
#   is terminus [bool] - this API lists terminus stations for each connection, which helps tremendously
#   typo [string] - link the misspelled destination to the real destination
#   intermediate stations [list of strings] - list the stations between origin and destination, allows for some cool
#           visualizations later
#
# Take this opportunity to restructure how the results are communicated, too:
# old way: {destination: [lon, lat, trip_duration]}
# Since many lookups are done, we want to keep it in a dict, but want the data inside to be more intuitive
# new way: {destination: {lon: lon, lat: lat, trip_duration: trip_duration, arrival_time: arrival_time,
#                           num_connections: num_connections

# Because jobs are spawned prior to the dict being filled in, a worker may be assigned to query
# a destination for which we already have a duration. Therefore, we pass in the entire data dict, allowing
# the worker to check before wasting a precious API query.

# Queries and processes the timetable.search.ch API
async def async_query_and_process(origin_details, destination_list, session):
    url = create_url([origin_details, '2021-06-25','7:00'], destination_list)

    t_init = time.time()
    async with session.get(url) as response:
        print(response)
        output_data_portion = await asyncio_process_response(response)
        td_get = time.time() - t_init
    return output_data_portion


# Takes in the origin details and list of destinations and creates an appropriate url to get
def create_url (origin_details, destination_list):
    prefix = 'https://timetable.search.ch/api/route.json?one_to_many=1'
    origin_body = '&from=' + origin_details[0] + '&date=' + origin_details[1] + '&time=' + origin_details[2]
    destination_body = ''
    for i in range(len(destination_list)):
        destination_body = destination_body + '&to[' + str(i) + ']=' + destination_list[i]
    url = prefix + origin_body + destination_body
    print(url)
    return url


# Processes the response using asyncio
async def asyncio_process_response(response):
    jdata = await response.json()
    output = process_response(response, jdata)
    print( "returning output")
    return output


# Processes response and converts the json into a list of destinations with coordinates and travel times
def process_response(response, jdata):
    data_portions = []
    if response.status != 200:
        print("ERROR: " + str(response.status) + ": " + str(jdata['errors'][0]['message']))
        if response.status == 429:
            exit()
        return 0
    else:
        if 'results' not in jdata:
            print("ERROR: API returned with no results.")
            return {}

    data_portions.append({jdata['results'][0]['points'][0]['text'] : {'destination': jdata['results'][0]['points'][0]['text'],
                                                      'lon': jdata['results'][0]['points'][0]['lon'],
                                                      'lat': jdata['results'][0]['points'][0]['lat'],
                                                      'departure': 0,
                                                      'arrival': 0,
                                                      'train_time': 0,
                                                      'num_transfers': 0,
                                                      'intermediate_stations': 0,
                                                      'endnode': 0,
                                                      'hovertext': jdata['results'][0]['points'][0]['text']
                                                      }})

    for i in range(len(jdata['results'])):  # iterate on the list of destinations given
        if 'connections' not in jdata['results'][i]:
            # if 'message' in jdata['results'][i]:
            #     data_portion = {jdata['results'][i]: {'error': jdata['results'][i]['message']}}
            # else:
            #     data_portion = {jdata['results'][i]: {'error': 'unknown error.'}}
            # data_portions.append(data_portion)
            continue
        for con in jdata['results'][i]['connections']:  # iterate on the connection for each destination
            # if con['departure'].split()[0] != origin_details[1]:
            #     continue
            data_portion = {}
            departure_time = datetime_to_timestamp(con['departure'])
            stop_count = 0
            for leg in range(len(con['legs'])):  # iterate on the legs for each connection
                end_node = 0
                if 'exit' in con['legs'][leg]:
                    if 'to' in con['legs'][leg]:
                        if con['legs'][leg]['exit']['name'] == con['legs'][leg]['to']: end_node = 1
                    data_portion[con['legs'][leg]['exit']['name']] = {'destination': con['legs'][leg]['exit']['name'],
                                                                      'lon': con['legs'][leg]['exit']['lon'],
                                                                      'lat': con['legs'][leg]['exit']['lat'],
                                                                      'departure': departure_time,
                                                                      'arrival': datetime_to_timestamp(
                                                                          con['legs'][leg]['exit']['arrival']),
                                                                      'train_time': datetime_to_timestamp(
                                                                          con['legs'][leg]['exit'][
                                                                              'arrival']) - departure_time,
                                                                      'num_transfers': leg - 1,
                                                                      'intermediate_stations': stop_count,
                                                                      'endnode': end_node,
                                                                      'hovertext': con['legs'][leg]['exit'][
                                                                                       'name'] + '<br>' + core_func.sec_to_hhmm(
                                                                          datetime_to_timestamp(
                                                                              con['legs'][leg]['exit'][
                                                                                  'arrival']) - departure_time)
                                                                      }
                if 'stops' not in con['legs'][leg]:
                    continue
                if ('departure' not in con['legs'][leg]) | (con['legs'][leg]['stops'] is None):
                    end_node = 0
                    if 'departure' not in con['legs'][leg]: end_node = 1
                    data_portion[con['legs'][leg]['name']] = {'destination': con['legs'][leg]['name'],
                                                              'lon': con['legs'][leg]['lon'],
                                                              'lat': con['legs'][leg]['lat'],
                                                              'departure': departure_time,
                                                              'arrival': datetime_to_timestamp(
                                                                  con['legs'][leg]['arrival']),
                                                              'train_time': datetime_to_timestamp(
                                                                  con['legs'][leg]['arrival']) - departure_time,
                                                              'num_transfers': leg - 1,
                                                              'intermediate_stations': stop_count,
                                                              'endnode': end_node,
                                                              'hovertext': con['legs'][leg][
                                                                               'name'] + '<br>' + core_func.sec_to_hhmm(
                                                                  datetime_to_timestamp(
                                                                      con['legs'][leg]['arrival']) - departure_time)
                                                              }
                    continue

                for stop in con['legs'][leg]['stops']:  # iterate on the stops for each leg
                    if 'arrival' not in stop:
                        continue
                    train_time = datetime_to_timestamp(stop['arrival']) - departure_time
                    if train_time < 86400:
                        data_portion[stop['name']] = {'destination': stop['name'],
                                                      'lon': stop['lon'],
                                                      'lat': stop['lat'],
                                                      'departure': departure_time,
                                                      'arrival': datetime_to_timestamp(stop['arrival']),
                                                      'train_time': train_time,
                                                      'num_transfers': leg,
                                                      'intermediate_stations': stop_count,
                                                      'endnode': 0,
                                                      'hovertext': stop['name'] + '<br>' + core_func.sec_to_hhmm(
                                                          train_time)
                                                      }
                        stop_count += 1
            data_portions.append(data_portion)

    # data portions contains many multiple entries; now go through and consolidate them
    # the dictionary with the shorted train_time will be kept; departure time is 2nd priority
    output_data_portion = {}
    for conn in data_portions:  # iterate through each data_portion (ie each connection)
        for city in conn:  # iterate through each destination
            if city not in output_data_portion:
                output_data_portion[city] = conn[city]
            elif conn[city]['train_time'] < output_data_portion[city]['train_time']:
                output_data_portion[city].update(conn[city])
            elif conn[city]['train_time'] == output_data_portion[city]['train_time']:
                if conn[city]['arrival'] < output_data_portion[city]['arrival']:
                    output_data_portion[city].update(conn[city])
            else:
                continue

    # if any of the data portions suggest a destination is not an endnode, then it's definitely not
    for city in output_data_portion:
        for conn in data_portions:
            if city in conn:
                if 'endnode' in conn[city]:
                    if conn[city]['endnode'] == 0:
                        output_data_portion[city]['endnode'] = 0
    return output_data_portion


def datetime_to_timestamp(datetime_str):
    return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").timestamp()


async def async_api_handler(origin_details, data_set_master, dest_per_query):
    t_init = time.time()
    n_queries = -(-len(data_set_master)//dest_per_query)  #ceiling integer division
    async with aiohttp.ClientSession() as session:
        print('Opening AsyncIO HTTP session.')
        destination_chunks = [list(data_set_master)[i:i + dest_per_query] for i in range(0, len(data_set_master), dest_per_query)]
        get_reqs = []
        for dest_list in destination_chunks:
            get_reqs.append(asyncio.ensure_future(async_query_and_process(origin_details, dest_list, session)))
        results_list = await asyncio.gather(*get_reqs)


    results = {}
    for result in results_list:
        results.update(result)
    print('Time to clear the stack: ' + str(time.time() - t_init) + ' seconds, and ' + str(len(destination_chunks)) + 'API queries')


    return results


if __name__ == "__main__":
    data_list = ['Bern', 'Thun', 'Interlaken Ost']
    origin_details = ['Zurich HB', '2021-06-25', '7:00']
    asyncio.run(async_api_handler(origin_details, data_list, 2 ))
    print('done')
