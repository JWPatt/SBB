from pymongo import MongoClient
from pprint import pprint
import pandas as pd
import io_func
import multiprocessing as mp


class MongodbHandler:
    def __init__(self, url, database_name):
        self.client = MongoClient(url)
        self.db = getattr(self.client, database_name)  # SBB_time_map
        # self.col = ''

        self.origins = []
        # for key in self.db_tree():
        #     self.origins.append(key)
        self.collections = self.db.list_collection_names()

    @classmethod
    def init_and_set_col(cls, url, database_name, col_name):
        mgdb = cls(url, database_name)
        # mgdb.set_col(col_name)
        print(col_name)
        mgdb.col = getattr(mgdb.db, col_name.replace(' ', '_').replace('-', '_').replace(':', '_'))

        return mgdb

    def set_col(self, col_name):
        self.col = getattr(self.db, col_name.replace(' ', '_').replace('-', '_').replace(':', '_'))

    # def write_data_line_to_mongodb(self, data_dict):
    #     print('writing')
    #     # self.time.insert_one({"destination": destination, "lon": data_list[1],
    #     #                       "lat": data_list[2], "travel_time": data_list[0]})
    #
    #     # data_dict = {'arrival': 1624603860.0,
    #     #               'departure': 1624597320.0,
    #     #               'destination': 'Interlaken Wwesttttt',
    #     #               'endnode': 0,
    #     #               'intermediate_stations': 2,
    #     #               'lat': 46.682623,
    #     #               'lon': 7.851453,
    #     #               'num_transfers': 1,
    #     #               'travel_time': 16540.0}
    #
    #     if self.col == '':
    #         print('Attempting to write to DB without an origin_details - DB doesn\'t know where to look!')
    #         input()
    #     elif 'destination' in data_dict:
    #         if data_dict['travel_time'] < 86400:
    #             if self.col.count_documents({'destination': data_dict['destination']}) == 0:
    #                 self.col.insert_one(data_dict)
    #             elif self.col.count_documents({'destination': data_dict['destination']}) == 1:
    #                 print('updating')
    #                 self.col.update_one({'destination': data_dict['destination'], 'travel_time':{"$gt":data_dict['travel_time']}}, {'$set':data_dict})
    #             elif self.col.count_documents({'destination': data_dict['destination']}) > 1:
    #                 print('deleting')
    #                 fastest_entry = list(self.col.find({'destination': data_dict['destination']}).sort('travel_time', 1).limit(1))[0]
    #                 self.col.delete_many({'destination': data_dict['destination'], '_id': {"$ne": fastest_entry['_id']}})
    #                 self.col.update_one({'destination': data_dict['destination'], 'travel_time': {"$gt": data_dict['travel_time']}}, {'$set': data_dict})


    def write_data_dict_of_dict(self,data_dict_of_dict):
        # for key in data_dict_of_dict:
        #     self.write_data_line_to_mongodb(data_dict_of_dict[key])

        batch = []
        for key in data_dict_of_dict:
            batch.append(data_dict_of_dict[key])
        print(type(self.col))
        print((self.col))
        self.col.insert_many(batch)


    def update_data_dict_of_dict(self,data_dict_of_dict):
        batch = []
        for key in data_dict_of_dict:
            self.col.replace_one({'destination':key},data_dict_of_dict[key])
            # self.col.update_many({'destination':{'$regex':''}},batch)


    def update_col_dataframe(self,data_dict_of_dict):
        batch = []
        for key in data_dict_of_dict:
            batch.append(data_dict_of_dict[key])
        self.col.insert_many(batch)

    # def write_data_dict_of_dict_multi(self, data_dict_of_dict, nthreads):
    #     pool = mp.pool.ThreadPool(nthreads)
    #     for key in data_dict_of_dict:
    #         result = pool.map(self.write_data_line_to_mongodb,data_dict_of_dict)
    #     pool.close()
    #     pool.join()




    # Display hierarchy of database destinations, dates, and times
    # Will be useful to show users which queries have results already (instead of waiting for new queries)
    # def db_tree(self):
    #     tree = {}
    #     for i in self.db.list_collection_names():
    #         num_pts = self.db[i].estimated_document_count()
    #         col = (i.split("."))
    #         if len(col)==2:
    #             if col[0] not in tree:
    #                 tree[col[0]] = {col[1]: {col[2]: num_pts}}
    #             else:
    #                 if col[1] not in tree[col[0]]:
    #                     tree[col[0]][col[1]] = {col[2]: num_pts}
    #                 else:
    #                     tree[col[0]][col[1]][col[2]] = num_pts
    #     return tree

    def get_all_data_list(self,origin_details=None):
        if origin_details is None:
            if self.col == '':
                print('Attempting to read from DB without origin_details - DB doesn\'t know where to look!')
                input()
            else:
                data = list(self.col.find())
        else:
            col = io_func.mongodb_loc(origin_details)
            print(self.col)
            data_ = getattr(self.db, col)
            data = list(data_.find())
        return data


    # Get data from db given an origin city, date, and time
    def get_data_list(self, origin_details=None):
        if origin_details is None:
            if self.col == '':
                print('Attempting to read from DB without origin_details - DB doesn\'t know where to look!')
                input()
            else:
                data = list(self.col.find({}, {'destination':1,
                                               'lat':1,
                                               'lon':1,
                                               'train_time':1,
                                               'drive_time':1,
                                               'drive_minus_train':1,
                                               'hovertext_train':1,
                                               'hovertext_drive':1,
                                               'hovertext_diff':1}))
        else:
            col = io_func.mongodb_loc(origin_details)
            print(self.col)
            data_ = getattr(self.db, col)
            data = list(data_.find())

        return data

    # Get data from db given an origin city, date, and time
    def get_all_data_dict(self, origin_details=None):
        if origin_details is None:
            if self.col == '':
                print('Attempting to read from DB without an origin_details - DB doesn\'t know where to look!')
                input()
            else:
                data = list(self.col.find())
        else:
            col = io_func.mongodb_loc(origin_details)
            print(self.col)
            data = getattr(self.db, col)
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
        data = list(data.find({},{'destination':1,'_id':0,'lat':1,'lon':1}))
        data_dict = {}
        for row in data:
            # would using row.pop('destination') be better here? Saves memory at the cost of speed.
            if 'destination' in row:
                data_dict[row['destination']] = row
        return data_dict


    # Get a set of known destinations from db given an origin city, date, and time
    def get_destination_set(self, origin_details=None):
        if origin_details is None:
            if self.col == '':
                print('Attempting to read from DB without an origin_details - DB doesn\'t know where to look!')
                input()
            else:
                data = list(self.col.find({}, {'destination':1, '_id':0}))
        else:
            col = io_func.mongodb_loc(origin_details)
            data_ = getattr(self.db, col)
            data = list(data_.find({},{'destination':1,'_id':0}))
        data_set = set()
        for row in data:
            if 'destination' in row:
                data_set.add(row['destination'])
        return data_set


# def write_data_dict_of_dict_multi(mgdb, data_dict_of_dict, nthreads):
#     pool = mp.Pool(nthreads)
#     for key in data_dict_of_dict:
#         result = pool.map(mgdb.write_data_line_to_mongodb,data_dict_of_dict[key])
#         # result.get()
#     pool.close()
#     pool.join()

# def write_data_line_to_mongodb(url, database_name, origin_details, data_dict):
#     client = MongoClient(url)
#     db = getattr(client, database_name)  # SBB_time_map
#     dest = getattr(db, origin_details[0].replace(' ', '_'))  # Destination
#     date = getattr(dest, origin_details[1].replace('-', '_'))  # Travel date
#     time = getattr(date, origin_details[2].replace(':', '_'))  # Travel time
#
#     if time == '':
#         print('Attempting to write to DB without an origin_details - DB doesn\'t know where to look!')
#         input()
#     elif 'destination' in data_dict:
#
#         # self.time.insert_one(data_dict)  # faster to just insert every time, but creates many duplicates
#
#         if data_dict['travel_time'] < 86400:
#             if time.count_documents({'destination': data_dict['destination']}) == 0:
#                 time.insert_one(data_dict)
#             elif time.count_documents({'destination': data_dict['destination']}) == 1:
#                 print('updating')
#                 time.update_one({'destination': data_dict['destination'],'travel_time':{"$gt":data_dict['travel_time']}}, {'$set':data_dict})
#             elif time.count_documents({'destination': data_dict['destination']}) > 1:
#                 print('deleting')
#                 fastest_entry = list(time.find({'destination': data_dict['destination']}).sort('travel_time', 1).limit(1))[0]
#                 time.delete_many({'destination': data_dict['destination'], '_id': {"$ne": fastest_entry['_id']}})
#                 time.update_one( {'destination': data_dict['destination'], 'travel_time': {"$gt": data_dict['travel_time']}}, {'$set': data_dict})
#
#
# def write_osrm_line_to_mongodb(url, database_name, origin_city, data_dict):
#     client = MongoClient(url)
#     db = getattr(client, database_name)  # SBB_time_map
#     dest = getattr(db, ('osrm_' + origin_city.replace(' ', '_')))  # Destination
#
#     if dest == '':
#         print('Attempting to write to DB without an origin_details - DB doesn\'t know where to look!')
#         input()
#     elif 'destination' in data_dict:
#
#         # self.time.insert_one(data_dict)  # faster to just insert every time, but creates many duplicates
#
#         if data_dict['travel_time'] < 86400:
#             if dest.count_documents({'destination': data_dict['destination']}) == 0:
#                 dest.insert_one(data_dict)
#             elif dest.count_documents({'destination': data_dict['destination']}) == 1:
#                 print('updating')
#                 dest.update_one({'destination': data_dict['destination'],'travel_time':{"$gt":data_dict['travel_time']}}, {'$set':data_dict})
#             elif dest.count_documents({'destination': data_dict['destination']}) > 1:
#                 print('deleting')
#                 fastest_entry = list(dest.find({'destination': data_dict['destination']}).sort('travel_time', 1).limit(1))[0]
#                 dest.delete_many({'destination': data_dict['destination'], '_id': {"$ne": fastest_entry['_id']}})
#                 dest.update_one( {'destination': data_dict['destination'], 'travel_time': {"$gt": data_dict['travel_time']}}, {'$set': data_dict})



if __name__ == "__main__":
    pw = pd.read_csv("secret_mgdb_pw_local.csv")
    print(pw.columns.to_list()[0])
    handler = MongodbHandler.init_and_set_col(pw, "SBB_time_map", ['Zurich HB', '2021-06-25', '7:00'])
    # pprint(handler.db_tree())
    print(handler.client.test)
    # pprint (handler.get_destination_set())

    # ['Zurich HB', '7:00', '2021-06-25']


