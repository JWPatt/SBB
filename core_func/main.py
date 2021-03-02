import multiprocessing as mp
import time
import os
import sys
import io_func
import core_func
from core_func.sbb_api import sbb_query_and_update
from core_func.sbb_api_2 import sbb_query_and_update_2
from pprint import pprint


def primary(origin_details, mgdb):

    if mp.cpu_count() < 2:
        print('Function not set up for less than 2 threads! Terminating.')
        return 0

    try:
        # Load file names
        dir_prefix = ''
        if __name__ == '__main__':
            dir_prefix = '../'

        main_table_csv = dir_prefix + io_func.database_loc('output_csvs/', origin_details)
        all_city_file_csv = dir_prefix + 'input_csvs/Betriebspunkt.csv'
        key_cities_csv = dir_prefix + 'input_csvs/key_cities_sbb_short.csv'
        bad_destinations_csv = dir_prefix + 'output_csvs/shitlist.csv'
        misspelled_destinations_csv = dir_prefix + 'output_csvs/typos.csv'
        extrema_destinations_csv = dir_prefix + 'output_csvs/extrema.csv'
        fresh_start = False

        if fresh_start:
            if os.path.isfile(main_table_csv):
                os.system("rm " + main_table_csv)
                os.system("touch " + main_table_csv)
            if os.path.isfile(bad_destinations_csv):
                os.system("rm " + bad_destinations_csv)
                os.system("touch " + bad_destinations_csv)
            if os.path.isfile(extrema_destinations_csv):
                os.system("rm " + extrema_destinations_csv)
                os.system("touch " + extrema_destinations_csv)
            if os.path.isfile(misspelled_destinations_csv):
                os.system("rm " + misspelled_destinations_csv)
                os.system("touch " + misspelled_destinations_csv)

        # Load parallel processing tools
        manager = mp.Manager()
        q = manager.Queue()
        pool = mp.Pool(4)

        duration_counter = 0
        data = manager.dict()
        # data = {}
        old_data = {}
        bad_destinations = set()
        misspelled_destinations = set()
        extrema_destinations = set()
        not_extrema_destinations = set()
        output_sets = [bad_destinations, misspelled_destinations, extrema_destinations, not_extrema_destinations]

        old_data.update(io_func.csv_to_dict(main_table_csv))
        print("Loading previous data of {old_data} cities.".format(old_data=str(len(old_data))))
        data.update(io_func.betriebspunkt_csv_to_empty_dict(all_city_file_csv))
        data.update(io_func.csv_to_empty_dict(key_cities_csv))
        data.update(old_data)

        bad_destinations.update(io_func.csv_to_set(bad_destinations_csv))
        misspelled_destinations.update(io_func.csv_to_set(misspelled_destinations_csv))
        extrema_destinations.update(io_func.csv_to_set(extrema_destinations_csv))

        n_extrema = len(extrema_destinations)
        n_misspelled = len(misspelled_destinations)
        n_bad = len(bad_destinations)

        jobs = []
        stack_counter = 0
        listener = pool.apply_async(core_func.listen_and_write, (main_table_csv, data, duration_counter,
                                                                 old_data, origin_details, q,))
        t_init = time.time()
        data_list_master = list(data)
        data_list_of_lists = [data_list_master[x:x+200] for x in range(0,len(data_list_master),200)]

        for data_list in data_list_of_lists[0:3]:
            job = pool.apply_async(sbb_query_and_update_2, (data_list, q, origin_details))
            jobs.append(job)
        print(len(jobs))
        results={}
        index = 0
        for job in jobs:
            index += 1
            data_portion, td_get = job.get()
            print(str(index) + ' got ' + str(len(data_portion)))
            results.update(data_portion)
            print(str(index) + ' total ' + str(len(results)))
            job = pool.apply_async(sbb_query_and_update_2, (data_list_of_lists[index+2], q, origin_details))
            jobs.append(job)

            #now need to make it so the new spawned jobs get each a unique list of cities not already known

            # mgdb.write_data_dict_of_dict(data_portion)

        # t_init = time.time()
        # data_list = []
        # counter = 0
        # skip_counter = 0
        # results = {}
        # for city in data_list_master:
        #     if counter < 200:
        #         if city not in results:
        #             data_list.append(city)
        #             counter += 1
        #         else:
        #             skip_counter += 1
        #     else:
        #         print('skipped over ', str(skip_counter))
        #         skip_counter = 0
        #         job = pool.apply_async(sbb_query_and_update_2, (data_list, q, origin_details))
        #         data_portion, td_get = job.get()
        #         # data_portion, td_get = sbb_query_and_update_2(data_list, '', origin_details)
        #         print("API: ", time.time() - t_init)
        #         # mgdb.write_data_dict_of_dict(data_portion)
        #         # print("mongodb: ", time.time() - t_init)
        #         results.update(data_portion)
        #         print('results length: ', str(len(results)))
        #         data_list = []
        #         counter = 0
        # mgdb.write_data_dict_of_dict(results)


        print('done')
        input()

        # t_init = time.time()
        # for data_list in data_list_of_lists:
        #     job = pool.apply_async(sbb_query_and_update_2, (data_list, q, origin_details))
        #     jobs.append(job)
        #     # collect results from the workers through the pool result queue
        #     print(time.time() - t_init)
        #
        # for job in jobs:
        #     data_portion, td_get = job.get()
        #     mgdb.write_data_dict_of_dict(data_portion)

        t_init = time.time()
        data_list = []
        counter = 0
        skip_counter = 0
        results = {}
        for city in data_list_master:
            if counter < 200:
                if city not in results:
                    data_list.append(city)
                    counter += 1
                else:
                    skip_counter += 1
            else:
                print('skipped over ', str(skip_counter))
                skip_counter = 0
                data_portion, td_get = sbb_query_and_update_2(data_list, '', origin_details)
                print("API: ", time.time() - t_init)
                mgdb.write_data_dict_of_dict(data_portion)
                print("mongodb: ", time.time() - t_init)
                results.update(data_portion)
                print('results length: ', str(len(results)))
                data_list = []
                counter = 0
        mgdb.write_data_dict_of_dict(results)


        # t_init = time.time()
        # for data_list in data_list_of_lists:
        #     data_portion, td_get = sbb_query_and_update_2(data_list,'',origin_details)
        #     print("API: ", time.time() - t_init)
        #     mgdb.write_data_dict_of_dict(data_portion)
        #     print("mongodb: ", time.time() - t_init)

        print('Time to clear the stack: ' + str(time.time()-t_init) + ' seconds')

        # now we are done, kill the listener
        q.put('kill')
        pool.close()
        pool.join()

        io_func.write_destination_set_to_csv(bad_destinations, bad_destinations_csv)
        io_func.write_destination_set_to_csv(misspelled_destinations, misspelled_destinations_csv)
        io_func.write_destination_set_to_csv(extrema_destinations, extrema_destinations_csv)
        print("Added %s, %s, and %s to bad, misspelled, and extrema desntination csvs." % (
            (len(bad_destinations) - n_bad),
            (len(misspelled_destinations) - n_misspelled),
            (len(extrema_destinations) - n_extrema)))

    except KeyboardInterrupt or EOFError:
        print("Killing process: writing extrema, misspelled, and bad destination csv's first.")
        if extrema_destinations:
            print("End node destination list: added " + str(len(extrema_destinations) - n_extrema) + " destinations to list.")
            io_func.write_destination_set_to_csv(extrema_destinations, extrema_destinations_csv)
        if misspelled_destinations:
            print("Misspelled destination list: added " + str(len(misspelled_destinations) - n_misspelled) + " destinations to list.")
            io_func.write_destination_set_to_csv(misspelled_destinations, misspelled_destinations_csv)
        if bad_destinations:
            print("Bad destination list: added " + str(len(bad_destinations) - n_bad) + " destinations to list.")
            io_func.write_destination_set_to_csv(bad_destinations, bad_destinations_csv)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(exc_type, fname, exc_tb.tb_lineno, e)
        raise

    return 1


if __name__ =="__main__":
    origin_details = ['Zurich HB', '2021-06-25', '7:09']
    mgdb = io_func.MongodbHandler("127.0.0.1:27017", "SBB_time_map")
    mgdb.set_col(['Zurich HB', '2021-06-25', '7:09'])

    t_init = time.time()
    primary(origin_details, mgdb)
    print(time.time() - t_init)