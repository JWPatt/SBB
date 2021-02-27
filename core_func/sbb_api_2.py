import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from pprint import pprint
import datetime

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
def sbb_query_and_update(destination_list, origin_details):
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
    retry = Retry(connect=1, backoff_factor=0.5)
    # adapter = HTTPAdapter(max_retries=retry)
    # session.mount('http://37.120.239.152:3128', adapter)
    # session.mount('https://37.120.239.152:3128', adapter)
    proxies = {
        "http": 'http://84.17.51.233:3128',
        "https": 'https://84.17.51.233:3128',
    }
    t_init = time.time()
    response = requests.get(url)
    td_get = time.time() - t_init
    # print(' took %f seconds.' % td_get)
    jdata = response.json()
    # pprint(jdata)
    # input()
    if response.status_code != 200:
        print("ERROR: " + str(response.status_code) + ": " + str(jdata['errors'][0]['message']))
        if response.status_code == 429:
            exit()
        return 0
    else:
        if 'results' not in jdata:
            print("ERROR: API returned with no results.")

    for i in range(len(jdata['results'])):  # iterate on the list of destinations given
        if 'connections' not in jdata['results'][i]:
            data_portion[i] = {destination_list[i]: jdata['results'][i]['message']}
            continue
        for con in jdata['results'][i]['connections']:  # iterate on the connection for each destination
            departure_time = datetime_to_timestamp(con['departure'])
            stop_count = 0
            for leg in range(len(con['legs'])):  # iterate on the legs for each connection
                print("leg number " + str(leg))
                if 'arrival' in con['legs'][leg]:
                    data_portion[con['legs'][leg]['name']] = {'destination': con['legs'][leg]['name'],
                                                  'lon': con['legs'][leg]['lon'],
                                                  'lat': con['legs'][leg]['lat'],
                                                  'arrival': datetime_to_timestamp(con['legs'][leg]['arrival']),
                                                  'travel_time': datetime_to_timestamp(
                                                      stop['arrival']) - departure_time,
                                                  'num_transfers': leg-1,
                                                  'intermediate_stations': stop_count
                                                  }
                    print(data_portion[con['legs'][leg]['name']])
                    continue

                for stop in con['legs'][leg]['stops']:  # iterate on the stops for each leg
                    print("stop: ", stop)
                    if 'arrival' not in stop:
                        continue
                    data_portion[stop['name']] = {'destination': stop['name'],
                                                  'lon': stop['lon'],
                                                  'lat': stop['lat'],
                                                  'arrival': datetime_to_timestamp(stop['arrival']),
                                                  'travel_time': datetime_to_timestamp(stop['arrival']) - departure_time,
                                                  'num_transfers': leg,
                                                  'intermediate_stations': stop_count
                                                  }
                    print(data_portion[stop['name']])
                    stop_count += 1

    return data_portion



    #
    # for t in range(len(jdata['connections'])):
    #     try:
    #         jdata['connections'][t]['sections'][0]['journey']['passList'][0]['departureTimestamp']
    #     except (KeyError, IndexError, TypeError, UnboundLocalError) as e:
    #         print(str(e))
    #         present = False
    #     else:
    #         present = True
    #     if present and not None:
    #         departure_time.append(jdata['connections'][t]['sections'][0]['journey']['passList'][0]['departureTimestamp'])
    #
    #     try:
    #         for i in range(0, len(jdata['connections'][t]['sections'])):
    #             if jdata['connections'][t]['sections'][i]['journey'] is None:
    #                 continue
    #             for j in range(1, len(jdata['connections'][t]['sections'][i]['journey']['passList'])):
    #                 if jdata['connections'][t]['sections'][i]['journey']['passList'][j]['arrivalTimestamp'] is None:
    #                     continue
    #
    #                 station = jdata['connections'][t]['sections'][i]['journey']['passList'][j]['station']['name']
    #                 x_coord = jdata['connections'][t]['sections'][i]['journey']['passList'][j]['station']['coordinate']['x']
    #                 y_coord = jdata['connections'][t]['sections'][i]['journey']['passList'][j]['station']['coordinate']['y']
    #                 dur = jdata['connections'][t]['sections'][i]['journey']['passList'][j]['arrivalTimestamp']-departure_time[t]
    #                 data_portion[station] = [x_coord, y_coord, dur]
    #                 true_destination = station
    #     except(KeyError) as e:
    #         print('Key Error: ' + str(e))
    #     except(IndexError) as e:
    #         print('Index Error: ' + str(e))
    #     except(TypeError) as e:
    #         print('Type Error: ' + str(e))
    #     except(UnboundLocalError) as e:
    #         print('Unbound Local Error: ' + str(e))
    #     data_portions.append(data_portion)
    #
    # output_data_portion = {}
    # try:
    #     for t in range(len(data_portions)):
    #         for key in data_portions[t]:
    #             if key:
    #                 if key not in output_data_portion or (data_portions[t][key][2] < output_data_portion[key][2]):
    #                     output_data_portion[key] = data_portions[t][key]
    #     if destination not in output_data_portion:
    #         output_data_portion[destination]=None
    #         if true_destination:
    #             destination = true_destination
    # except (TypeError) as e:
    #     print('TypeError: ' + str(e) + " key is " + key + " destination is " + destination, t, output_data_portion)
    #
    # # if destination has a typo, create valid duration for both the typo name and corrected name
    # # this prevents future searches of the typo'd name.
    # # if jdata['to'] is not None:
    # #     if destination != jdata['to']['name']:
    # #         destination = jdata['to']['name']  # remove the typo from subseqeunt csvs
    #
    #
    # return destination, output_data_portion, td_get


def datetime_to_timestamp(datetime_str):
    return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").timestamp()

# API return json structure

#zurich, data['connections'][0]['sections'][i]['journey']['passList'][j]['departureTimestamp']
"""
{ connections
    [ 
        { from:
          to:
          duration:
          sections:
            [
              { journey:
                  { passList:
                    [
                      { station:
                          { id:
                            name:
                            coordinate:
                                { x: ##
                                  y: ##
                        departureTimestamp: ##              #zurich, data['connections'][0]['sections'][i]['journey']['passList'][j]['departureTimestamp']
                      { station:
                          { id:
                            name:                           first stop, data['connections'][0]['sections'][i]['journey']['passList'][j+1]['station']['name']
                            coordinate:
                                { x: ##                     first stop, data['connections'][0]['sections'][i]['journey']['passList'][j+1]['station']['coordinate']['x']
                                  y: ##
                        arrivalTimestamp = ##               first stop, data['connections'][0]['sections'][i]['journey']['passList'][j+1]['arrivalTimestamp']
                      { station:
                          { id:
                            name:
                            coordinate:
                                { x: ##
                                  y: ##
                        arrivalTimestamp = ##               #second stop, data['connections'][0]['sections'][i]['journey']['passList'][j+2]['arrivalTimestamp']
              { journey:                                    #the second leg of the connection
                  { passList:
                    [
                      { station:
                          { id:
                            name:
                            coordinate:
                                { x: ##
                                  y: ##
                        arrivalTimestamp: ##                #this is the same as the arrivalTimestamp of the last station of the previous leg
                        departureTimestamp: ##              #this isn't important to us
                      { station:
                          { id:
                            name:
                            coordinate:
                                { x: ##
                                  y: ##
                        arrivalTimestamp = ##               #first stop, data['connections'][0]['sections'][i+1]['journey']['passList'][j+1]['arrivalTimestamp']
                      { station:
                          { id:
                            name:
                            coordinate:
                                { x: ##
                                  y: ##
                        arrivalTimestamp = ##               #second stop, data['connections'][0]['sections'][i+1]['journey']['passList'][j+2]['arrivalTimestamp']


"""

if __name__ == "__main__":
    idk = (sbb_query_and_update(['Chur','fdsafas','Winterthur'],['Zurich HB', '2021-06-25','7:00']))
    pprint(idk)

