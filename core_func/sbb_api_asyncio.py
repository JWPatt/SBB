import time
import datetime
import core_func
import aiohttp
import asyncio


async def async_query_and_process(_origin_details, destination_list, session):
    """Queries and processes results from the timetable.search.ch API

    Args:
        _origin_details: A list containing: [0] origin location, [1] date, and [2] starting time
        destination_list: A list of destinations to be submitted in a single API query
        session: The HTTP session (can be an Asyncio HTTP session)

    Returns:
        dict: A dictionary of the processed results from a single API request
    """

    # Must supply a time and date. Saturday at 7:00 is a realistic time for hikers to begin.
    travel_start_date = '2021-06-25'
    travel_start_time = '7:00'

    url = create_url([_origin_details, travel_start_date, travel_start_time], destination_list)

    async with session.get(url) as response:
        output_data_portion = await asyncio_process_response(response)

    return output_data_portion


def create_url(_origin_details, destination_list):
    """Takes in the origin details and list of destinations and creates the timetable.search.ch url to query

    Args:
        _origin_details: A list containing: [0] origin location, [1] date, and [2] starting time
        destination_list: A list of destinations to be submitted in a single API query

    Returns:
        str: A URL to be used to query the timetable.search.ch API; supports multiple destinations per query
    """
    prefix = 'https://timetable.search.ch/api/route.json?one_to_many=1'

    origin_body = f'&from={_origin_details[0]}&date={_origin_details[1]}&time={_origin_details[2]}'

    # Build iteratively with necessary syntax between destinations
    destination_body = ''
    for i, dest in enumerate(destination_list):
        destination_body = f'{destination_body}&to[{i}]={dest}'

    return f'{prefix}{origin_body}{destination_body}'


async def asyncio_process_response(response):
    """Wraps the process_response function for use with asyncio (must use "await" keyword). Appears redundant,
    but is necessary for asyncio to work correctly.

    Args:
        response: The raw API response

    Returns:
        json: A dictionary of the processed results from a single API request (via process_response)
    """
    # Simply awaiting the response throws a TypeError
    jdata = await response.json()
    return process_response(response, jdata)


def process_response(response, jdata):
    """Processes response and json reponse into a list of destinations with coordinates and travel times.

    Args:
        response: The raw API response
        jdata: JSONified API response

    Returns:
        A dictionary of the processed results from a single API request
    """
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

    data_portions.append({jdata['results'][0]['points'][0]['text']:
                         {'destination': jdata['results'][0]['points'][0]['text'],
                          'lon': jdata['results'][0]['points'][0]['lon'],
                          'lat': jdata['results'][0]['points'][0]['lat'],
                          'departure': 0,
                          'arrival': 0,
                          'train_time': 0,
                          'num_transfers': 0,
                          'intermediate_stations': 0,
                          'endnode': 0,
                          'hovertext': jdata['results'][0]['points'][0]['text'],
                          }})

    # Iterate on the list of destinations given
    for i in range(len(jdata['results'])):
        if 'connections' not in jdata['results'][i]:
            continue

        # iterate on the connection for each destination
        for con in jdata['results'][i]['connections']:
            data_portion = {}
            departure_time = datetime_to_timestamp(con['departure'])
            stop_count = 0

            # iterate on the legs for each connection
            for leg in range(len(con['legs'])):
                end_node = 0
                if 'exit' in con['legs'][leg]:
                    if 'to' in con['legs'][leg]:
                        if con['legs'][leg]['exit']['name'] == con['legs'][leg]['to']:
                            end_node = 1
                    data_portion[con['legs'][leg]['exit']['name']] = \
                        {'destination': con['legs'][leg]['exit']['name'],
                         'lon': con['legs'][leg]['exit']['lon'],
                         'lat': con['legs'][leg]['exit']['lat'],
                         'departure': departure_time,
                         'arrival': datetime_to_timestamp(con['legs'][leg]['exit']['arrival']),
                         'train_time': datetime_to_timestamp(con['legs'][leg]['exit']['arrival']) - departure_time,
                         'num_transfers': leg - 1,
                         'intermediate_stations': stop_count,
                         'endnode': end_node,
                         'hovertext': con['legs'][leg]['exit']['name'] + '<br>' + core_func.sec_to_hhmm(
                             datetime_to_timestamp(con['legs'][leg]['exit']['arrival']) - departure_time)
                         }

                if 'stops' not in con['legs'][leg]:
                    continue

                if ('departure' not in con['legs'][leg]) | (con['legs'][leg]['stops'] is None):
                    end_node = 0
                    if 'departure' not in con['legs'][leg]:
                        end_node = 1
                    data_portion[con['legs'][leg]['name']] = \
                        {'destination': con['legs'][leg]['name'],
                         'lon': con['legs'][leg]['lon'],
                         'lat': con['legs'][leg]['lat'],
                         'departure': departure_time,
                         'arrival': datetime_to_timestamp(con['legs'][leg]['arrival']),
                         'train_time': datetime_to_timestamp(con['legs'][leg]['arrival']) - departure_time,
                         'num_transfers': leg - 1,
                         'intermediate_stations': stop_count,
                         'endnode': end_node,
                         'hovertext': con['legs'][leg]['name'] + '<br>' +
                            core_func.sec_to_hhmm(datetime_to_timestamp(con['legs'][leg]['arrival']) - departure_time)
                         }
                    continue

                for stop in con['legs'][leg]['stops']:  # iterate on the stops for each leg
                    if 'arrival' not in stop:
                        continue
                    train_time = datetime_to_timestamp(stop['arrival']) - departure_time
                    if train_time < 86400:
                        data_portion[stop['name']] = \
                            {'destination': stop['name'],
                             'lon': stop['lon'],
                             'lat': stop['lat'],
                             'departure': departure_time,
                             'arrival': datetime_to_timestamp(stop['arrival']),
                             'train_time': train_time,
                             'num_transfers': leg,
                             'intermediate_stations': stop_count,
                             'endnode': 0,
                             'hovertext': f"{stop['name']}<br>{core_func.sec_to_hhmm(train_time)}",
                             }
                        stop_count += 1
            data_portions.append(data_portion)

    # Data portions contains many multiple entries; delete duplicates (while minimizing train_time)
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

    # If the city is not an endnode in any of the entries, then flag the destination as not an endnode
    for city in output_data_portion:
        for conn in data_portions:
            if city in conn:
                if 'endnode' in conn[city]:
                    if conn[city]['endnode'] == 0:
                        output_data_portion[city]['endnode'] = 0
    return output_data_portion


def datetime_to_timestamp(datetime_str):
    """
    Converts a date&time string to datetime format
    Args:
        datetime_str (str): String of date & time in this format: "YYYY-MM-DD HH:MM:SS"

    Returns:
        datetime: Datetime value of the input string
    """
    return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").timestamp()


async def async_api_handler(_origin_details, data_set_master, dest_per_query):
    """Queries SBB API, processes response, and returns dictionary of locations with travel information.

    Args:
        _origin_details: A list containing: [0] origin location, [1] date, and [2] starting time
        data_set_master: A list of all destinations, to be submitted piece-wise in multiple API queries
        dest_per_query: The number of destinations to submit per API query (timetable.search.ch has max of ~220)

    Returns:
        dict (str: dict): The processed and compiled results of all API queries. Keys are destination names; nested
            dicts contain relevant data: travel time, lat/lon, # of stops, etc.
    """
    t_init = time.time()
    async with aiohttp.ClientSession() as session:
        print('Opening AsyncIO HTTP session.')

        # Break up list of destinations into chunks of a particular size (the SBB API has a ceiling around 210)
        destination_chunks = [list(data_set_master)[i:i + dest_per_query] for i in range(0, len(data_set_master), dest_per_query)]
        get_requests = []
        for dest_list in destination_chunks:
            get_requests.append(asyncio.ensure_future(async_query_and_process(_origin_details, dest_list, session)))
        print(f'Awaiting response from {len(get_requests)} requests.')
        results_list = await asyncio.gather(*get_requests)

    results = {}
    for result in results_list:
        results.update(result)

    print(f'{len(destination_chunks)} API queries took {time.time() - t_init} seconds to receive and process')
    return results


if __name__ == "__main__":
    data_list = ['Bern', 'Thun', 'Interlaken Ost']
    origin_details = ['Zurich HB', '2021-06-25', '7:00']
    asyncio.run(async_api_handler(origin_details, data_list, 2))
