import unittest
from core_func.osrm import osrm_build_url, osrm_query_one
import requests


class TestOSRMModule(unittest.TestCase):
    """Test for the OSRM querying module"""

    osrm_base_url = "http://127.0.0.1:5000"
    origin_latlon = {'lat': 47.3769, 'lon': 8.5417}
    dest_values = {'lat': 46.9480, 'lon': 7.4474}

    osrm_url = osrm_build_url(osrm_base_url, origin_latlon, dest_values)

    session = requests.Session()

    def test_osrm_build_url(self):
        osrm_url_correct = 'http://127.0.0.1:5000/route/v1/driving/8.5417,47.3769;7.4474,46.948?steps=false'
        self.assertEqual(self.osrm_url, osrm_url_correct)

    def test_osrm_response_time(self):
        response = self.session.get(self.osrm_url, timeout=1)
        jdata = response.json()
        self.assertEqual(jdata['code'], 'Ok')
        self.assertGreater(jdata['routes'][0]['duration'], 0)

    def test_osrm_query_one(self):
        duration = osrm_query_one(self.osrm_url, self.session)
        duration_correct = 5399.2
        self.assertEqual(duration, duration_correct)


if __name__ == '__main__':
    unittest.main()
