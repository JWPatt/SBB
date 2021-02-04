# Because jobs are spawned prior to the dict being filled in, a worker may be assigned to query
# a destination for which we already have a duration. Therefore, we pass in the entire data dict, allowing
# the worker to check before wasting a precious API query.

def update_master_table_multi(destination, data,q):

    if data[destination] is not None:
        return destination, {destination: None}

    print('API query for ' + destination )
    import requests
    response = requests.get('https://transport.opendata.ch/v1/connections?from=Zurich&to='+destination+'&date=2021-06-25&time=7:00&limit=3')
    print(response.status_code)
    jdata = response.json()
    if response.status_code != 200:
        print("ERROR: " + str(response.status_code) + ": " + str(jdata['errors'][0]['message']))
        if response.status_code == 429:
            input()
        return destination, {destination: None}

    # with open("/Users/Patterson/Documents/Python/test/sample_sbb_api.txt") as f:
    #     jdata = json.load(f)
    #     print(type(f))
    data_portions = []
    data_portion = {}
    departure_time = []
    try:
        jdata['to']['name']
        data_portion[destination] = None
    except (KeyError, IndexError, TypeError, UnboundLocalError):
        present = False

    #a mispelled station may still give results; remove it so we don't throw it into the shitlist.
    # if jdata['to'] is not None:
    #     # destination = jdata['to']['name']     # commenting this out prevents typo'd stations being re-API'd
    #     print ('destination is not none' + str(destination))
    # else: data_portion[destination] = None

    # print('searching for ' + destination + ' and finding ' + str(jdata['to']))


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
        # except(TypeError):
        #     print('Type Error')
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
        print('TypeError, sbb_api_lookup_connection_multi, line 79')
        # print('returning ' + destination + " and " + str({destination: None}))
        # return destination, {destination: None}

    # if destination has a typo, create valid duration for both the typo name and corrected name
    # this prevents future searches of the typo'd name.
    if jdata['to'] is not None:
        if destination != jdata['to']['name']:
            # data_portion[destination] = data_portion[jdata['to']['name']]
            # print("changing " + destination + " to " + str(jdata['to']['name']))
            destination = jdata['to']['name']  # remove the typo from subseqeunt csvs
    print("returning " + destination + " and " + str(data_portion))
    return destination, data_portion


# def check_portion_against_data_and_write(data_portion, data, openfile):
#     for key in data_portion:
#         if key not in data:
#             data[key] = data_portion[key]
#             write_data_line(key, data[key], openfile)
#         elif data[key] is None:
#             data[key] = data_portion[key]
#             write_data_line(key, data[key], openfile)
#     openfile.flush()






# old_dict = {'Zurich':[20, 50, 100]}
# print(old_dict)
# update_master_table_multi(old_dict, 'Rosenlaui')
# print(old_dict.keys())
# print(old_dict.values())



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
