import unittest
import requests

class TestStringMethods(unittest.TestCase):

    # def __init__(self):
    session = requests.Session()

    origin_details = ['Zurich HB', '2021-06-25', '7:00']
    destination_list = ['Bern', 'Thun', 'Interlaken Ost']
    prefix = 'https://timetable.search.ch/api/route.json?one_to_many=1'

    origin_body = '&from=' + origin_details[0] + '&date=' + origin_details[1] + '&time=' + origin_details[2]

    destination_body = ''
    for i in range(len(destination_list)):
        destination_body = destination_body + '&to[' + str(i) + ']=' + destination_list[i]

    url = prefix + origin_body + destination_body

    response = session.get(url)
    jdata = response.json()



    def test_api_2_get(self):


        self.assertEqual(self.response.status_code,200)


if __name__ == '__main__':
    unittest.main()