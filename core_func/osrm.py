import time
import requests


def osrm_query(origin_city, city_latlon_dict, osrm_url, req_session):
    """This script queries and processes the response from the Open Streetmap Routing Machine.

    Args:
        origin_city (str): Origin city
        city_latlon_dict (dict of dict): Dictionary of lat/lon coordinates, with destination cities as keys
        osrm_url (str): URL of the OSRM service
        req_session (requests.Session): HTTP session

    Returns:
        dict of dict: Dictionary of destinations, lat/lon coordinates, and drive times
    """
    try:
        origin_latlon = city_latlon_dict[origin_city]
    except KeyError:
        raise KeyError("The Origin city is not a key within the city data dict. Check the spelling (special characters"
                       "especially) and capitalization.")

    count = 0
    return_dict = dict(city_latlon_dict)
    for dest_city, dest_values in city_latlon_dict.items():
        while True:
            try:
                count += 1
                query_url = f"{osrm_url}/route/v1/driving/{origin_latlon['lon']},{origin_latlon['lat']};" \
                            f"{dest_values['lon']},{dest_values['lat']}?steps=false"

                response = req_session.get(query_url)
                jdata = response.json()
                return_dict[dest_city] = {}
                if response.status_code == 200:
                    city_latlon_dict[dest_city]['drive_time'] = jdata['routes'][0]['duration']
                break
            except ConnectionError:
                continue

    return return_dict


