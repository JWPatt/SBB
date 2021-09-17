from plotly import graph_objs as go


def get_hist_graph(hist_x_vals, colorbar, option_dropdown):
    # Currently these are not flexible, unfortunately
    n_bins = 28
    n_bins_diff = 24

    bin_min = min(colorbar[option_dropdown]['intervals'])
    bin_max = max(colorbar[option_dropdown]['intervals'])

    hist_graph = go.Histogram(x=hist_x_vals,
                         marker=dict(
                             color=colorbar[option_dropdown]['colors_histogram'],
                             cmax=bin_max,
                             cmin=bin_min,
                         ),
                         hoverinfo="x",
                         xbins=dict(
                             start=min(colorbar[option_dropdown]['intervals']) if option_dropdown != 3 else bin_min,
                             end=max(colorbar[option_dropdown]['intervals']) if option_dropdown != 3 else bin_min,
                             size=(max(colorbar[option_dropdown]['intervals'])
                                   - min(colorbar[option_dropdown]['intervals']))
                                  / (n_bins if option_dropdown < 2 else n_bins_diff)
                            ),
                         ),

    return hist_graph
