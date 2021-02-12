def database_loc(origin_details):
    main_table_csv = 'example_results/' + origin_details[0].replace(' ', '_') \
                     + '_' + str(origin_details[1]) \
                     + '_' + str(origin_details[2]) + '.csv'
    return main_table_csv
