from pymongo import MongoClient
from pprint import pprint
import pandas as pd


class MongodbHandler:
    def __init__(self, url, database_name):
        self.client = MongoClient(url)
        self.db = getattr(self.client, database_name)  # SBB_time_map
        self.dest = ''
        self.date = ''
        self.time = ''

        self.origins = []
        for key in self.db_tree():
            self.origins.append(key)

        self.collections = self.db.list_collection_names()

    @classmethod
    def init_and_set_col(cls, url, database_name, origin_details):
        mgdb = cls(url, database_name)
        mgdb.dest = getattr(mgdb.db, origin_details[0].replace(' ', '_'))  # Destination
        mgdb.date = getattr(mgdb.dest, origin_details[1].replace('-', '_'))  # Travel date
        mgdb.time = getattr(mgdb.date, origin_details[2].replace(':', '_'))  # Travel time
        return mgdb

    def set_col(self, origin_details):
        self.dest = getattr(self.db, origin_details[0].replace(' ', '_'))  # Destination
        self.date = getattr(self.dest, origin_details[1].replace('-', '_'))  # Travel date
        self.time = getattr(self.date, origin_details[2].replace(':', '_'))  # Travel time

    def write_data_line_to_mongodb(self, destination, data_list):
        self.time.insert_one({"destination": destination, "travel_time": data_list[0],
                              "x_coord": data_list[1], "y_coord": data_list[2]})

    # Display hierarchy of database destinations, dates, and times
    # Will be useful to show users which queries have results already (instead of waiting for new queries)
    def db_tree(self):
        tree = {}
        for i in self.db.list_collection_names():
            num_pts = self.db[i].estimated_document_count()
            col = (i.split("."))
            if col[0] not in tree:
                tree[col[0]] = {col[1]: {col[2]: num_pts}}
            else:
                if col[1] not in tree[col[0]]:
                    tree[col[0]][col[1]] = {col[2]: num_pts}
                else:
                    tree[col[0]][col[1]][col[2]] = num_pts
        return tree



if __name__ == "__main__":
    handler = MongodbHandler("127.0.0.1:27017", "SBB_time_map", ["test","test","test2"])
    pprint(handler.db_tree())

    # ['Zurich HB', '7:00', '2021-06-25']


