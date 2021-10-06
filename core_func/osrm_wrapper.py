import io_func
import pandas as pd
import core_func
import requests


def osrm_wrapper(origin_city, location_dict):
    """Calculates drive times from an origin city to multiple destinations.

    Args:
        origin_city (str): Starting location (location must exist in the sbb_results argument with lat/lon values
        location_dict (dict of dict): Destinations as keys, with 'lat' and 'lon' key/values for each destination

    Returns:
        dict of dict: Updated input dictionary with 'drive_time' values
    """
    session = requests.Session()
    osrm_url = 'http://127.0.0.1:5000'
    location_dict = core_func.osrm_query_many(origin_city, location_dict, osrm_url, session)

    # for key, value in sbb_results.items():
    #     if 'drive_time' not in value:
    #         print(f'{key} has no OSRM drive time!')

    return location_dict