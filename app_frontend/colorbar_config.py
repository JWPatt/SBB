import core_func
import numpy as np

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

    for i in range(0, 3):
        colorbar[i]['input'] = core_func.discrete_colorscale(colorbar[i]['intervals'], colorbar[i]['colors'])
        colorbar[i]['bvals'] = np.array(colorbar[i]['intervals'])
        colorbar[i]['tickvals'] = [np.mean(colorbar[i]['intervals'][k:k + 2]) * 60 * 60 for k in range(
            len(colorbar[i]['intervals']) - 1)]  # position with respect to bvals where ticktext is displayed
        # print(colorbar[i]['tickvals'])
        # print(colorbar[i]['bvals'])
        if i < 2:
            colorbar[i]['ticktext'] = [f'<{colorbar[i]["bvals"][1]}'] + [
                f'{colorbar[i]["bvals"][k]}-{colorbar[i]["bvals"][k + 1]}' for k in
                range(1, len(colorbar[i]["bvals"]) - 2)] + [f'>{colorbar[i]["bvals"][-2]}']
        else:
            colorbar[i]['ticktext'] = [f'More than {colorbar[i]["bvals"][1]}<br>hour slower'] + [
                f'{colorbar[i]["bvals"][k]} to {colorbar[i]["bvals"][k + 1]}' for k in
                range(1, len(colorbar[i]["bvals"]) - 2)] + [f'More than {colorbar[i]["bvals"][-2]}<br>hour faster']


    return colorbar