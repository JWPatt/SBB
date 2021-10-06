import time
import requests
import sys
import json
from io_func import status_bar_printer


def osrm_query_one(query_url, req_session):
    """Submits query to OSRM service and extracts the duration (in seconds).
    NB: the origin and destination names must be exact. "Zurich HB" != "Zürich HB"


    Args:
        query_url (str): URL to send to OSRM service
        req_session (requests.Session): HTTP session

    Returns:
        int: Drive time from origin to destination (in seconds)
    """
    response = req_session.get(query_url, timeout=1)
    try:
        jdata = response.json()
        if response.status_code == 200:
            return jdata['routes'][0]['duration']
    except json.decoder.JSONDecodeError:
        pass


def osrm_build_url(osrm_base_url, origin_latlon, dest_values):
    """Formats the URL to be used with the OSRM service.
    
    Args:
        osrm_base_url (str): Base URL for OSRM (e.g. "http://127.0.0.1:5000")
        origin_latlon (dict): Dictionary containing latitude & longitude information for the origin city
        dest_values (dict): Dictionary containing latitude & longitude information for the destination city

    Returns:
        str: A URL that can be sent to the OSRM service
    """
    return f"{osrm_base_url}/route/v1/driving/{origin_latlon['lon']},{origin_latlon['lat']};" \
           f"{dest_values['lon']},{dest_values['lat']}?steps=false"


def status_bar_printer(count, n_destinations):
    """Prints status of OSRM queries: percentage and # of queries.

    Args:
        count (int): The number of queries performed already
        n_destinations (int): The number of total destinations to be queried

    Returns:
        None - prints status bar, percentage completion, and # of queries performed
    """
    sys.stdout.write('\r')
    progress = count / n_destinations * 20
    sys.stdout.write("[%-20s] %d%% - No. queries: %i" % ('=' * int(progress), progress * 5, count))
    sys.stdout.flush()


def osrm_query_many(origin_city, city_latlon_dict, osrm_base_url, req_session):
    """This script queries and processes the response from the Open Streetmap Routing Machine.

    Args:
        origin_city (str): Origin city
        city_latlon_dict (dict of dict): Dictionary of lat/lon coordinates, with destination cities as keys
        osrm_base_url (str): URL of the OSRM service
        req_session (requests.Session): HTTP session

    Returns:
        dict of dict: Dictionary of destinations, lat/lon coordinates, and drive times
    """
    try:
        origin_latlon = city_latlon_dict[origin_city]
    except KeyError:
        raise KeyError(f'The Origin city ({origin_city}) is not a key within the city data dict.'
                       f'Check the spelling (special characters especially) and capitalization.')

    count = 0
    connection_error_count = 0
    connection_error_destinations = []
    n_destinations = len(city_latlon_dict.keys())
    t_init = time.time()
    for dest_city, dest_values in city_latlon_dict.items():
        while True:
            try:
                count += 1
                query_url = osrm_build_url(osrm_base_url, origin_latlon, dest_values)
                try:
                    city_latlon_dict[dest_city]['drive_time'] = osrm_query_one(query_url, req_session)
                except json.decoder.JSONDecodeError:
                    raise

                # I am willing to suffer some slowdown (~1 sec per 2000 queries) to keep an eye on progress
                status_bar_printer(count, n_destinations)
                break

            # Sometimes the connection fails. It appears random, working the next minute. Save them and try again later.
            except ConnectionError:
                connection_error_count += 1
                connection_error_destinations.append(dest_city)
            except requests.exceptions.ReadTimeout:
                connection_error_count += 1
                connection_error_destinations.append(dest_city)

    print(f'\nTotal OSRM compute time: {time.time() - t_init} seconds.')

    # Try a second time to get these missed values.
    if len(connection_error_destinations) > 0:
        print(f'Total of {connection_error_count} connection errors --> and therefore missing data!')
        for dest_city in connection_error_destinations:
            print(f'Retrying query for {dest_city}')
            query_url = osrm_build_url(osrm_base_url, origin_latlon, city_latlon_dict[dest_city])
            city_latlon_dict[dest_city]['drive_time'] = osrm_query_one(query_url, req_session)
            if 'drive_time' in city_latlon_dict[dest_city]:
                connection_error_count += -1
        if len(connection_error_destinations) > 0:
            print(f'Total of {connection_error_count} connection errors remaining!')

    return city_latlon_dict




