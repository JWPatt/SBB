def colorbar_config():
    colorbar = {0: {}, 1: {}, 2: {}}

    colorbar[0]['intervals'] = [0, 1, 2, 3, 4, 5, 6, 7]
    colorbar[0]['colors'] = ['#000000', '#0c2a50', '#593d9c', '#a65c85', '#de7065', '#f9b641', '#e8fa5b'][::-1]
    colorbar[0]['colors_histogram'] = ['#000000', '#000000', '#000000', '#000000', '#0c2a50', '#0c2a50', '#0c2a50',
                                       '#0c2a50', '#593d9c', '#593d9c', '#593d9c', '#593d9c', '#a65c85', '#a65c85',
                                       '#a65c85', '#a65c85', '#de7065', '#de7065', '#de7065', '#de7065', '#f9b641',
                                       '#f9b641', '#f9b641', '#f9b641', '#e8fa5b', '#e8fa5b', '#e8fa5b', '#e8fa5b'][
                                      ::-1]
    colorbar[0]['title'] = "Travel Time - hours"
    colorbar[1]['intervals'] = [0, 1, 2, 3, 4, 5, 6, 7]
    colorbar[1]['colors'] = ['#000000', '#0c2a50', '#593d9c', '#a65c85', '#de7065', '#f9b641', '#e8fa5b'][::-1]
    colorbar[1]['colors_histogram'] = ['#000000', '#000000', '#000000', '#000000', '#0c2a50', '#0c2a50', '#0c2a50',
                                       '#0c2a50', '#593d9c', '#593d9c', '#593d9c', '#593d9c', '#a65c85', '#a65c85',
                                       '#a65c85', '#a65c85', '#de7065', '#de7065', '#de7065', '#de7065', '#f9b641',
                                       '#f9b641', '#f9b641', '#f9b641', '#e8fa5b', '#e8fa5b', '#e8fa5b', '#e8fa5b'][
                                      ::-1]
    colorbar[1]['title'] = colorbar[0]['title']
    colorbar[2]['intervals'] = [-1.5, -1.0, -0.5, -0.25, 0, 0.25, 0.5, 1.0, 1.5]
    colorbar[2]['colors'] = ['#67001F', '#C13639', '#F09C7B', '#FBE3D4', '#DBEAF2', '#87BEDA', '#2F79B5', '#053061'][
                            ::-1]
    colorbar[2]['colors_histogram'] = ['#67001F', '#67001F', '#67001F', '#67001F', '#C13639', '#C13639', '#C13639',
                                       '#C13639', '#F09C7B', '#F09C7B', '#FBE3D4', '#FBE3D4', '#DBEAF2', '#DBEAF2',
                                       '#87BEDA', '#87BEDA', '#2F79B5', '#2F79B5', '#2F79B5', '#2F79B5', '#053061',
                                       '#053061', '#053061', '#053061'][::-1]
    # colorbar[2]['colors'] = ['#5c0900', '#cc1500', '#ff7a6b', '#ffb1a8', '#6677ff', '#384eff', '#0101c6', '#000075'][::-1]
    colorbar[2]['title'] = "Difference (public transport minus driving time) - Hours"

    return colorbar