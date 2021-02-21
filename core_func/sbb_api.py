import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Because jobs are spawned prior to the dict being filled in, a worker may be assigned to query
# a destination for which we already have a duration. Therefore, we pass in the entire data dict, allowing
# the worker to check before wasting a precious API query.
def sbb_query_and_update(destination, data, q, origin_details):
    if data[destination] is not None:
        return destination, {destination: data[destination]}, 0

    data_portions = []
    data_portion = {}
    input_destination = {}
    true_destination = ""
    departure_time = []
    # print('API query for %s... ' % destination)
    t_init = time.time()
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://37.120.239.152:3128', adapter)
    session.mount('https://37.120.239.152:3128', adapter)
    proxy = {
        "https": 'https://37.120.239.150:3128',
        "http": 'http://37.120.239.150:3128'
    }
    url = 'https://transport.opendata.ch/v1/connections?from=%s&to=%s&date=%s&time=%s&limit=3' \
          % (origin_details[0], destination, origin_details[1], origin_details[2])
    response = requests.get(url)
    td_get = time.time() - t_init
    # print(' took %f seconds.' % td_get)
    jdata = response.json()
    if response.status_code != 200:
        print("ERROR: " + str(response.status_code) + ": " + str(jdata['errors'][0]['message']))
        if response.status_code == 429:
            input()
        return destination, {}, 0
    else:
        try:
            jdata['to']['name']
            input_destination[destination] = None  # important step for correctly catching misspelled destinations
        except (KeyError, IndexError, TypeError, UnboundLocalError) as e:
            present = False
            print("ERROR: API response is null for %s - check the API URL: %s" %(destination, str(e)))
            return destination, {}, 0

    if not jdata['connections']:
        print("Bad destination: %s" % (destination))
        return destination, {}, 0

    for t in range(len(jdata['connections'])):
        try:
            jdata['connections'][t]['sections'][0]['journey']['passList'][0]['departureTimestamp']
        except (KeyError, IndexError, TypeError, UnboundLocalError) as e:
            print(str(e))
            present = False
        else:
            present = True
        if present and not None:
            departure_time.append(jdata['connections'][t]['sections'][0]['journey']['passList'][0]['departureTimestamp'])

        try:
            for i in range(0, len(jdata['connections'][t]['sections'])):
                if jdata['connections'][t]['sections'][i]['journey'] is None:
                    continue
                for j in range(1, len(jdata['connections'][t]['sections'][i]['journey']['passList'])):
                    if jdata['connections'][t]['sections'][i]['journey']['passList'][j]['arrivalTimestamp'] is None:
                        continue

                    station = jdata['connections'][t]['sections'][i]['journey']['passList'][j]['station']['name']
                    x_coord = jdata['connections'][t]['sections'][i]['journey']['passList'][j]['station']['coordinate']['x']
                    y_coord = jdata['connections'][t]['sections'][i]['journey']['passList'][j]['station']['coordinate']['y']
                    dur = jdata['connections'][t]['sections'][i]['journey']['passList'][j]['arrivalTimestamp']-departure_time[t]
                    data_portion[station] = [x_coord, y_coord, dur]
                    true_destination = station
        except(KeyError) as e:
            print('Key Error: ' + str(e))
        except(IndexError) as e:
            print('Index Error: ' + str(e))
        except(TypeError) as e:
            print('Type Error: ' + str(e))
        except(UnboundLocalError) as e:
            print('Unbound Local Error: ' + str(e))
        data_portions.append(data_portion)

    output_data_portion = {}
    try:
        for t in range(len(data_portions)):
            for key in data_portions[t]:
                if key:
                    if key not in output_data_portion or (data_portions[t][key][2] < output_data_portion[key][2]):
                        output_data_portion[key] = data_portions[t][key]
        if destination not in output_data_portion:
            output_data_portion[destination]=None
            if true_destination:
                destination = true_destination
    except (TypeError) as e:
        print('TypeError: ' + str(e) + " key is " + key + " destination is " + destination, t, output_data_portion)

    # if destination has a typo, create valid duration for both the typo name and corrected name
    # this prevents future searches of the typo'd name.
    # if jdata['to'] is not None:
    #     if destination != jdata['to']['name']:
    #         destination = jdata['to']['name']  # remove the typo from subseqeunt csvs


    return destination, output_data_portion, td_get



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
    dest, data, idk = (sbb_query_and_update("Hoch-Ybrig", {"Hoch-Ybrig":None}, "q", ['Zurich HB', '7:00', '2021-06-25']))

