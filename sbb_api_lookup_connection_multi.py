import requests


# Because jobs are spawned prior to the dict being filled in, a worker may be assigned to query
# a destination for which we already have a duration. Therefore, we pass in the entire data dict, allowing
# the worker to check before wasting a precious API query.
def update_master_table_multi(destination, data, q):
    if data[destination] is not None:
        return destination, {destination: data[destination]}

    data_portions = []
    data_portion = {}
    departure_time = []

    print('API query for ' + destination )
    response = requests.get('https://transport.opendata.ch/v1/connections?from=Zurich&to='+destination+'&date=2021-06-25&time=7:00&limit=3')
    jdata = response.json()

    if response.status_code != 200:
        print("ERROR: " + str(response.status_code) + ": " + str(jdata['errors'][0]['message']))
        if response.status_code == 429:
            input()
        return destination, {destination: None}
    else:
        try:
            print(jdata['to']['name'])
            jdata['to']['name']
            if jdata['to'] is None:
                print("ERROR: API response is null - check the API URL")
                return destination, {destination: None}
            else:
                data_portion[destination] = None
        except (KeyError, IndexError, TypeError, UnboundLocalError):
            present = False
            print("ERROR: API response is null - check the API URL")
            input()

    for t in range(len(jdata['connections'])):
        try:
            jdata['connections'][t]['sections'][0]['journey']['passList'][0]['departureTimestamp']
        except (KeyError, IndexError, TypeError, UnboundLocalError):
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
                    # print("i is " +str(i)+", j is " + str(j))
                    # print(jdata['connections'][t]['sections'][i]['journey']['passList'][j]['arrivalTimestamp'])
                    if jdata['connections'][t]['sections'][i]['journey']['passList'][j]['arrivalTimestamp'] is None:
                        continue

                    station = jdata['connections'][t]['sections'][i]['journey']['passList'][j]['station']['name']
                    x_coord = jdata['connections'][t]['sections'][i]['journey']['passList'][j]['station']['coordinate']['x']
                    y_coord = jdata['connections'][t]['sections'][i]['journey']['passList'][j]['station']['coordinate']['y']
                    dur = jdata['connections'][t]['sections'][i]['journey']['passList'][j]['arrivalTimestamp']-departure_time[t]
                    # print(station + ' ' + str(x_coord) + ' ' + str(y_coord) + ' ' + str(dur))
                    data_portion[station] = [x_coord, y_coord, dur]
        except(KeyError):
            print('Key Error')
        except(IndexError):
            print('Index Error')
        except(TypeError):
            print('Type Error')
        except(UnboundLocalError):
            print('Unbound Local Error')
        data_portions.append(data_portion)

    try:
        output_data_portion = {}
        for t in range(len(data_portions)):
            for key in data_portions[t]:
                if key is not None:
                    if key not in output_data_portion or data_portions[t][key][2] < output_data_portion[key][2]:
                        output_data_portion[key] = data_portions[t][key]
    except (TypeError):
        print('TypeError, sbb_api_lookup_connection_multi')

    # if destination has a typo, create valid duration for both the typo name and corrected name
    # this prevents future searches of the typo'd name.
    if jdata['to'] is not None:
        if destination != jdata['to']['name']:
            destination = jdata['to']['name']  # remove the typo from subseqeunt csvs

    return destination, data_portion



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
