from pymongo import MongoClient
from pprint import pprint


class MongodbHandler:
    def __init__(self, url, database_name, origin_details):
        self.client = MongoClient(url)
        self.db = getattr(self.client, database_name)  # SBB_time_map
        self.dest = getattr(self.db, origin_details[0].replace(' ', '_'))  # Destination
        self.date = getattr(self.dest, origin_details[1].replace('-', '_'))  # Travel date
        self.time = getattr(self.date, origin_details[2].replace(':', '_'))  # Travel time

    def write_data_line_to_mongodb(self, destination, data_list):
        self.time.insert_one({"destination": destination, "travel_time": data_list[0],
                              "x_coord": data_list[1], "y_coord":data_list[2]})


if __name__ == "__main__":
    handler = MongodbHandler("127.0.0.1:27017", "SBB_time_map", ["test","test","test2"])  # ['Zurich HB', '7:00', '2021-06-25']
    handler.write_data_line_to_mongodb()


