import multiprocessing as mp
import time
import os
import sys
import io_func
import core_func
from html_plot import make_html_map


def main(origin_details):

    if mp.cpu_count() < 2:
        print('Function not set up for less than 2 threads! Terminating.')
        return 0

    try:
        # Load file names
        main_table_csv = io_func.database_loc('output_csvs/', origin_details)
        all_city_file_csv = 'input_csvs/Betriebspunkt_short.csv'
        key_cities_csv = 'input_csvs/key_cities_sbb.csv'
        bad_destinations_csv = 'output_csvs/shitlist.csv'
        misspelled_destinations_csv = 'output_csvs/typos.csv'
        extrema_destinations_csv = 'output_csvs/extrema.csv'
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
        listener = pool.apply_async(core_func.listen_and_write, (main_table_csv, data, duration_counter, old_data, q,))
        t_init = time.time()

        for key in sorted(list(data), key=lambda x: 1):
            if key in bad_destinations or key in misspelled_destinations:
                continue
            if data[key] is None:
                extrema_destinations.add(key)
                stack_counter += 1
                print('Adding ' + key + ' to Pool.')
                job = pool.apply_async(sbb_query_and_update, (key, data, q, origin_details))
                jobs.append(job)
                if stack_counter == 50000:
                    break
        print('%d cities have been loaded onto the stack.' % stack_counter)
        print('Time to load stack: %d seconds' % (time.time()-t_init))

        # collect results from the workers through the pool result queue
        t_init = time.time()
        for job in jobs:
            try:
                # execute the SBB api get request and process the json
                destination, data_portion, td_get = job.get()

                # compare the results with the previous results and sort data
                core_func.process_data(destination, data_portion, td_get, output_sets, q)

            except EOFError:
                print("Ran out of free API requests")
                break
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno, e)
                raise

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


if __name__ == "__main__":

    # Enter city name with or without special characters (probably safer without)
    # Enter time in HH:MM format (e.g. '13:10')
    # Enter date in YYYY-MM-DD format (e.g. '2021-11-22')
    origin_city = ['Zurich HB', 'Bern', 'Geneva']
    origin_time = ['7:00','7:00','7:00']
    origin_date = ['2021-06-25','2021-06-25','2021-06-25']
    origin_details = [[origin_city[i], origin_time[i], origin_date[i]] for i in range(3)]
    try:
        for i in origin_details[:1]:
            success = main(i)
            if success:
                data_csv = io_func.database_loc('output_csvs/', i)
                make_html_map(data_csv, i)
    except KeyboardInterrupt or EOFError:
        print("Killed by user.")
    except:
        raise
