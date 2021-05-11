import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pprint import pprint
import datetime
import core_func


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
def sbb_query_and_update_2(destination_list, q, origin_details, session):
    # if data[destination] is not None:
    #     return destination, {destination: data[destination]}, 0

    data_portions = []
    data_portion = {}
    input_destination = {}
    true_destination = ""
    departure_time = []
    # print('API query for %s... ' % destination)

    prefix = 'https://timetable.search.ch/api/route.json?one_to_many=1'
    origin_body = '&from=' + origin_details[0] + '&date=' + origin_details[1] + '&time=' + origin_details[2]
    destination_body = ''
    for i in range(len(destination_list)):
        destination_body = destination_body + '&to[' + str(i) + ']=' + destination_list[i]
    url = prefix + origin_body + destination_body
    print(url)

    # session = requests.Session()
    # retry = Retry(connect=1, backoff_factor=0.5)
    # adapter = HTTPAdapter(max_retries=retry)
    # session.mount('http://37.120.239.152:3128', adapter)
    # session.mount('https://37.120.239.152:3128', adapter)
    # proxies = {
    #     "http": 'http://84.17.51.233:3128',
    #     "https": 'https://84.17.51.233:3128',
    # }
    t_init = time.time()
    response = session.get(url)
    td_get = time.time() - t_init
    jdata = response.json()
    if response.status_code != 200:
        print("ERROR: " + str(response.status_code) + ": " + str(jdata['errors'][0]['message']))
        if response.status_code == 429:
            exit()
        return 0
    else:
        if 'results' not in jdata:
            print("ERROR: API returned with no results.")
            return {},td_get

    for i in range(len(jdata['results'])):  # iterate on the list of destinations given
        if 'connections' not in jdata['results'][i]:
            if 'message' in jdata['results'][i]:
                data_portion = {destination_list[i]: {'error': jdata['results'][i]['message']}}
            else:
                data_portion = {destination_list[i]: {'error': 'unknown error.'}}
            data_portions.append(data_portion)
            continue
        for con in jdata['results'][i]['connections']:  # iterate on the connection for each destination
            if con['departure'].split()[0] != origin_details[1]:
                continue
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
                                                          'arrival': datetime_to_timestamp(con['legs'][leg]['exit']['arrival']),
                                                          'travel_time': datetime_to_timestamp(
                                                              con['legs'][leg]['exit']['arrival']) - departure_time,
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
                    if 'departure' not in con['legs'][leg]: end_node = 1
                    data_portion[con['legs'][leg]['name']] = {'destination': con['legs'][leg]['name'],
                                                           'lon': con['legs'][leg]['lon'],
                                                              'lat': con['legs'][leg]['lat'],
                                                              'departure': departure_time,
                                                              'arrival': datetime_to_timestamp(con['legs'][leg]['arrival']),
                                                              'travel_time': datetime_to_timestamp(con['legs'][leg]['arrival']) - departure_time,
                                                              'num_transfers': leg - 1,
                                                              'intermediate_stations': stop_count,
                                                              'endnode': end_node,
                                                              'hovertext': con['legs'][leg]['name'] + '<br>' + core_func.sec_to_hhmm(
                                                                  datetime_to_timestamp(con['legs'][leg]['arrival']) - departure_time)
                                                              }
                    continue


                for stop in con['legs'][leg]['stops']:  # iterate on the stops for each leg
                    if 'arrival' not in stop:
                        continue
                    travel_time = datetime_to_timestamp(stop['arrival']) - departure_time
                    if travel_time < 86400:
                        data_portion[stop['name']] = {'destination': stop['name'],
                                                      'lon': stop['lon'],
                                                      'lat': stop['lat'],
                                                      'departure': departure_time,
                                                      'arrival': datetime_to_timestamp(stop['arrival']),
                                                      'travel_time': travel_time,
                                                      'num_transfers': leg,
                                                      'intermediate_stations': stop_count,
                                                      'endnode': 0,
                                                      'hovertext': stop['name'] + '<br>' + core_func.sec_to_hhmm(travel_time)
                                                      }
                        stop_count += 1
            data_portions.append(data_portion)

    # data portions contains many multiple entries; now go through and consolidate them
    # the dictionary with the shorted travel_time will be kept; departure time is 2nd priority
    output_data_portion = {}
    for conn in data_portions:  # iterate through each data_portion (ie each connection)
        for city in conn:  # iterate through each destination
            if city not in output_data_portion:
                output_data_portion[city] = conn[city]
            elif conn[city]['travel_time'] < output_data_portion[city]['travel_time']:
                output_data_portion[city].update(conn[city])
            elif conn[city]['travel_time'] == output_data_portion[city]['travel_time']:
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

    return output_data_portion, td_get


def datetime_to_timestamp(datetime_str):
    return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").timestamp()


if __name__ == "__main__":
    session = requests.Session()
    test = (sbb_query_and_update_2(['Bern', 'Thun', 'Interlaken Ost'], 'q', ['Zurich HB', '2021-06-25', '7:00'], session))
    pprint(test)
