import unittest
import requests
import core_func.sbb_api_asyncio
import json
import pandas as pd
import aiohttp
import asyncio

class TestStringMethods(unittest.TestCase):

    # def __init__(self):
    session = requests.Session()

    origin_details = ['Zurich HB', '2021-06-25', '7:00']
    destination_list = ['Bern', 'Thun', 'Interlaken Ost']

    url = core_func.sbb_api_asyncio.create_url(origin_details, destination_list)

    response = session.get(url)
    jdata = response.json()

    # with open('api_get_json.txt', 'w') as outfile:
    #     json.dump(jdata, outfile)

    with open('api_get_json.txt') as infile:
        jdata_test_template = json.load(infile)

    results = await core_func.sbb_api_asyncio.process_response(response)
    pd.DataFrame(results).to_json('processed_json.txt')



    def test_create_api2_url(self):
        self.assertEqual(True, isinstance(self.url, str))

    def test_api_2_get(self):
        self.assertEqual(self.response.status_code,200)

    def test_jdata(self):
        self.assertEqual(self.jdata_test_template, self.jdata)

    # def test_process_api2_response(self):







if __name__ == '__main__':
    unittest.main()