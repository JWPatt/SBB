from pymongo import MongoClient
import io_func


class MongodbHandler:
    """Class to handle MongoDB read and write actions.

    Args:
        url (str): URL to the MongoDB server
        database_name (str): name of the database to be used

    Attributes:
        client (pymongo.MongoClient): the MongoDB client
        db (pymongo database): the MongoClient database object (database name = origin city)
        collection: the MongoClient collection of documents (collection name = destiation city)
    """
    def __init__(self, url, database_name):
        self.client = MongoClient(url)
        self.db = self.client[database_name]

    @classmethod
    def init_and_set_col(cls, url, database_name, col_name):
        mgdb = cls(url, database_name)
        mgdb.set_col(col_name)
        return mgdb

    def set_col(self, col_name):
        if type(col_name) == str:
            self.collection = getattr(self.db, col_name.replace(' ', '_').replace('-', '_').replace(':', '_'))

    def write_data_dict_of_dict(self, data_dict_of_dict):
        batch = []
        for key in data_dict_of_dict:
            batch.append(data_dict_of_dict[key])
        self.collection.insert_many(batch)

    def update_data_dict_of_dict(self, data_dict_of_dict):
        for key in data_dict_of_dict:
            self.collection.replace_one({'destination': key}, data_dict_of_dict[key])

    # Get data from db given an origin city, date, and time
    def get_data_list(self, origin_details=None):
        if origin_details is None:
            if self.collection == '':
                print('Attempting to read from DB without origin_details - DB doesn\'t know where to look!')
                input()
            else:
                return list(self.collection.find({}, {'destination': 1,
                                                      'lat': 1,
                                                      'lon': 1,
                                                      'train_time': 1,
                                                      'drive_time': 1,
                                                      'drive_minus_train': 1,
                                                      'hovertext_train': 1,
                                                      'hovertext_drive': 1,
                                                      'hovertext_diff': 1,
                                                      }
                                                 )
                            )
        else:
            collection = io_func.reformat_origin_details(origin_details)
            data_ = getattr(self.db, collection)
            return list(data_.find())

    # Get data from db given an origin city, date, and time
    def get_all_data_dict(self, origin_details=None):
        if origin_details is None:
            if self.collection == '':
                print('Attempting to read from DB without an origin_details - DB doesn\'t know where to look!')
                input()
            else:
                data = list(self.collection.find())
        else:
            collection = io_func.reformat_origin_details(origin_details)
            data = getattr(self.db, collection)
            data = list(data.find())
        data_dict = {}

        for row in data:
            # would using row.pop('destination') be better here? Saves memory at the cost of speed.
            data_dict[row['destination']] = row

        return data_dict

    # Get set of end-node destinations from db given a collection name
    def get_endnode_set(self, col):
        data = getattr(self.db, col)
        data = list(data.find())
        data_set = set()
        for row in data:
            data_set.add(row['destination'])
        return data_set

    # Get dict of end-node destinations from db given a collection name
    def get_endnode_dict(self, col):
        data = getattr(self.db, col)
        data = list(data.find({},{'destination': 1, '_id': 0, 'lat': 1, 'lon': 1}))
        data_dict = {}
        for row in data:
            # would using row.pop('destination') be better here? Saves memory at the cost of speed.
            if 'destination' in row:
                data_dict[row['destination']] = row
        return data_dict

    # Get a set of known destinations from db given an origin city, date, and time
    def get_destination_set(self, origin_details=None):
        if origin_details is None:
            if self.collection == '':
                print('Attempting to read from DB without an origin_details - DB doesn\'t know where to look!')
                input()
            else:
                data = list(self.collection.find({}, {'destination': 1, '_id': 0}))
        else:
            collection = io_func.reformat_origin_details(origin_details)
            data_ = getattr(self.db, collection)
            data = list(data_.find({}, {'destination': 1, '_id': 0}))
        data_set = set()
        for row in data:
            if 'destination' in row:
                data_set.add(row['destination'])
        return data_set
