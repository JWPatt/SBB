import io_func
import sys
import os

# This function is poorly organized, but my priorities lie elsewhere.
# Determines which of the new results in data_portion belong in the bad_destinations, misspelled_destinations,
# extrema_destinations, or not_extrema_destinations sets.
# For example, a misspelled destination will likely return meaningful results, but will have a None for the values
# associated with that city name key; a bad destination will return an empty data_portion.


def process_data(destination, data_portion, td_get, output_sets, q):
    if not data_portion:  # if it doesn't exist, it goes to bad_destinations
        if not destination:
            print("Exceeded API call limit.")
            exit()
        else:
            output_sets[0].add(destination)  # bad_destinations
            output_sets[2].discard(destination)  # extrema_destinations
            print("API call resulted in a bad destination: " + destination)
    else:
        for key in list(data_portion):
            if data_portion[key] is None:
                if key != destination:
                    output_sets[1].add(key)  # misspelled_destinations
                    if key not in output_sets[3]:  # not_extrema_destinations
                        output_sets[2].add(destination)  # extrema_destinations
                else:
                    output_sets[2].add(destination)  # extrema_destinations
                del data_portion[key]
            if key in output_sets[2]:  # extrema_destinations
                if destination != key:
                    output_sets[2].discard(  # extrema_destinations
                        key)  # if this key is not the final destination, it cannot be an extrema
                    output_sets[2].add(destination)  # extrema_destinations
        if data_portion:
            q.put((destination, data_portion, td_get))
    return 0


# Listener thread remains here and catches new data and writes it continuously.
# Is it necessary? No, but I wanted to implement it and it's kind of fun.
# It is even less necessary if using a database (rather than local csvs) or a tool to catch errors
# and ensure data output, even when the code fails.

def listen_and_write(main_table_csv, data, duration_counter, old_data, origin_details, q):
    with open(main_table_csv, 'w', encoding='utf-8') as openfile:

        mgdb = io_func.MongodbHandler.init_and_set_col("127.0.0.1:27017", "SBB_time_map", origin_details)

        while 1:
            try:
                gotten = q.get()
                if gotten == 'kill':
                    break
                else:
                    data_portion = gotten[0]
                    td_get = gotten[1]
                # print('in while 1', data_portion, td_get)
                chain_counter = 0
                for key in list(data_portion):
                    if data_portion[key] is None:
                        continue
                    else:
                        if key not in data:
                            data[key] = data_portion[key]
                            mgdb.write_data_line_to_mongodb(key, data[key])
                            chain_counter += 1
                        elif data[key] is None:
                            data[key] = data_portion[key]
                            mgdb.write_data_line_to_mongodb(key, data[key])
                            chain_counter += 1
                duration_counter += chain_counter

                print('{:<30} | {:>3} new durations  | {:>6} total durations  |  {:0.2f} API response time'
                      .format(destination, chain_counter, duration_counter, td_get))
            except EOFError:
                print("Ran out of free API requests")
                return
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno, e)
                print(key, chain_counter, duration_counter, td_get)
                raise


def listen_and_spawn_job(data_list_master, origin_details, q):
    mgdb = io_func.MongodbHandler.init_and_set_col("127.0.0.1:27017", "SBB_time_map", origin_details)
    data_set_master = set(data_list_master)
    next_batch = []
    print('listener')
    while 1:
        # try:
            gotten = q.get()

            print('listener again')
            if gotten == 'kill':
                break
            else:
                data_portion = gotten[0]
                index = gotten[1]

            counter = 0
            for key in data_set_master:
                if key in data_portion:
                    data_set_master.remove(key)
                    print('removing ',str(key))
                elif counter < 1:
                    next_batch.append(key)
                    counter += 1
                    print('adding ', str(key))
                else:
                    print('exiting ', str(key))
                    counter = 0
                    break



        # except EOFError:
        #     print("Ran out of free API requests")
        #     raise
        # except Exception as e:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     print(exc_type, fname, exc_tb.tb_lineno, e)
        #     # print(key, chain_counter, duration_counter, td_get)
        #     raise

if __name__ == "__main__":
    process_data("Bern", {"Bern":1}, 0, [set(), set(), set(), set()], 'q')
