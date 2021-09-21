def get_dropdown_locations():
    # List of origin locations in Switzerland
    dropdown_locations = {
        "Zürich HB": {"lat": 47.3779, "lon": 8.5403},
        "Basel SBB": {"lat": 47.5596, "lon": 7.5886},
        "Bern": {"lat": 46.9490, "lon": 7.4385},
        "Chur": {"lat": 46.8508, "lon": 9.5320},
        "Genève": {"lat": 46.2044, "lon": 6.1413},
        "Lausanne": {"lat": 46.5197, "lon": 6.6323},
        "Lugano": {"lat": 46.0037, "lon": 8.9511},
        "Schwyz": {"lat": 47.0207, "lon": 8.6530},
        "Sion": {"lat": 46.2331, "lon": 7.3606},
        "St. Gallen": {"lat": 47.4245, "lon": 9.3767},
    }
    return dropdown_locations


def get_dropdown_maps(options_list):
    if len(options_list) != 3:
        raise ValueError('Function get_dropdown_maps is only configured for 3 options')
    else:
        hovertext_cols = {options_list[0]: 'hovertext_train',
                          options_list[1]: 'hovertext_drive',
                          options_list[2]: 'hovertext_diff'}
        travel_time_cols = {options_list[0]: 'train_time',
                            options_list[1]: 'drive_time',
                            options_list[2]: 'drive_minus_train'}
    return hovertext_cols, travel_time_cols
