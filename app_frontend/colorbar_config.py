import core_func
import numpy as np


def colorbar_config(n_same_color_bins):
    colorbar = {0: {}, 1: {}, 2: {}}

    colorbar[0]['title'] = "Travel Time - hours"
    colorbar[0]['intervals'] = [0, 1, 2, 3, 4, 5, 6, 7]
    colorbar[0]['colors'] = ['#000000', '#0c2a50', '#593d9c', '#a65c85', '#de7065', '#f9b641', '#e8fa5b'][::-1]

    colorbar[1] = colorbar[0]

    colorbar[2]['title'] = "Difference (public transport minus driving time) - Hours"
    colorbar[2]['intervals'] = [-1.5, -1.0, -0.5, -0.25, 0, 0.25, 0.5, 1.0, 1.5]
    colorbar[2]['colors'] = ['#67001F', '#C13639', '#F09C7B', '#FBE3D4', '#DBEAF2', '#87BEDA', '#2F79B5', '#053061'][
                            ::-1]

    # Plotly histogram requires a color value be given to each bin (no general/flexible option is available)
    # The histogram looks better with more than simply 8 bins, but we still want to limit it to 8 colors
    # Therefore, multiple bins will feature the same colors, and this loop creates the full list of colors for bins.
    for key in colorbar:
        colorbar[key]['colors_histogram'] = [j for j in colorbar[key]['colors'] for i in range(n_same_color_bins)]

    # TODO: the difference map's colorbar is nonlinear, so needs some other implementation to become generalized
    colorbar[2]['colors_histogram'] = ['#67001F', '#67001F', '#67001F', '#67001F', '#C13639', '#C13639', '#C13639',
                                       '#C13639', '#F09C7B', '#F09C7B', '#FBE3D4', '#FBE3D4', '#DBEAF2', '#DBEAF2',
                                       '#87BEDA', '#87BEDA', '#2F79B5', '#2F79B5', '#2F79B5', '#2F79B5', '#053061',
                                       '#053061', '#053061', '#053061'][::-1]

    for i in range(3):
        colorbar[i]['input'] = core_func.discrete_colorscale(colorbar[i]['intervals'], colorbar[i]['colors'])
        colorbar[i]['bvals'] = np.array(colorbar[i]['intervals'])
        colorbar[i]['tickvals'] = [np.mean(colorbar[i]['intervals'][k:k + 2]) * 60 * 60 for k in range(
            len(colorbar[i]['intervals']) - 1)]  # position with respect to bvals where ticktext is displayed
        if i < 2:
            colorbar[i]['ticktext'] = [f'<{colorbar[i]["bvals"][1]}'] + [
                f'{colorbar[i]["bvals"][k]}-{colorbar[i]["bvals"][k + 1]}' for k in
                range(1, len(colorbar[i]["bvals"]) - 2)] + [f'>{colorbar[i]["bvals"][-2]}']
        else:
            colorbar[i]['ticktext'] = [f'More than {colorbar[i]["bvals"][1]}<br>hour(s) slower'] + [
                f'{colorbar[i]["bvals"][k]} to {colorbar[i]["bvals"][k + 1]}' for k in
                range(1, len(colorbar[i]["bvals"]) - 2)] + [f'More than {colorbar[i]["bvals"][-2]}<br>hour(s) faster']
    return colorbar
