def database_loc(path, origin_details):
    main_table_csv = path + origin_details[0].replace(' ', '_') \
                     + '_' + str(origin_details[1]) \
                     + '_' + str(origin_details[2]) + '.csv'
    return main_table_csv


def mongodb_loc(origin_details):
    main_table_csv = origin_details[0].replace(' ', '_') \
                     + '.' + str(origin_details[1]).replace('-', '_') \
                     + '.' + str(origin_details[2]).replace(':', '_')
    return main_table_csv
