import unittest
from unittest import mock
import requests
import core_func.sbb_api_asyncio
import json
import pandas as pd
import aiohttp
import asyncio

class TestStringMethods(unittest.TestCase):

    # def __init__(self):
    session = requests.Session()

    origin_details = 'Zurich HB'
    travel_start_date = '2021-06-25'
    travel_start_time = '7:00'
    destination_list = ['Bern', 'Thun', 'Interlaken Ost']

    url = core_func.sbb_api_asyncio.create_url(origin_details, travel_start_date, travel_start_time, destination_list)

    # response = session.get(url)
    # jdata = response.json()

    # Uncomment to set the response json file to which we compare the API's response
    # with open('api_get_json.json', 'w') as outfile:
    #     json.dump(jdata, outfile)

    # Load the json to which we compare the API's response
    with open('api_get_json.txt') as infile:
        jdata_test_template = json.load(infile)


    with session.get(url) as response:
        output_data_portion = core_func.asyncio_process_response(origin_details, response)
        print('.', end='')



    # processed_results = asyncio.run(core_func.sbb_api_asyncio.process_response(origin_details, response, jdata_test_template))
    # print(processed_results)

    # Uncomment to set the processed response json file to which we compare the APIs response
    # with open('api_get_json.json', 'w') as outfile:
    #     json.dump(jdata, outfile)


    # results = asyncio.run(core_func.sbb_api_asyncio.async_api_handler(origin_details, data_set_master, dest_per_query))
    # pd.DataFrame(results).to_json('processed_json.txt')



    def test_create_api_url(self):
        self.assertEqual(True, isinstance(self.url, str))

    def test_api_get(self):
        self.assertEqual(self.response.status_code,200)

    def test_jdata(self):
        self.assertEqual(self.jdata_test_template, self.jdata)

    # def test_process_api2_response(self):







if __name__ == '__main__':
    unittest.main()