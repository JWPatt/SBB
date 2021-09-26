def reformat_origin_details(origin_details):
    main_table_csv = origin_details[0].replace(' ', '_') \
                     + '.' + str(origin_details[1]).replace('-', '_') \
                     + '.' + str(origin_details[2]).replace(':', '_')
    return main_table_csv
