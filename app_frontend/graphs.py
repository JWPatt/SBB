from plotly import graph_objs as go
from plotly.graph_objs import Scattermapbox


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


def get_mapbox_graph(sbb, hovertext_cols, options_list, option_dropdown, colorbar, travel_time_cols,
                     dropdown_locations=None):
    cmin = min(colorbar[option_dropdown]['intervals'])*3600
    cmax = max(colorbar[option_dropdown]['intervals'])*3600

    mapbox_graph = [Scattermapbox(
        lat=sbb["lat"],
        lon=sbb["lon"],
        mode="markers",
        hoverinfo='text',
        hovertext=sbb[hovertext_cols[options_list[option_dropdown]]],
        text=sbb[hovertext_cols[options_list[option_dropdown]]],
        marker=dict(
            showscale=True,
            color=sbb[travel_time_cols[options_list[option_dropdown]]],
            opacity=0.85,
            size=7.5,
            colorscale=colorbar[option_dropdown]['input'],
            cmax=cmax,
            cmin=cmin,
            colorbar=dict(
                title=colorbar[option_dropdown]['title'],
                x=0.035,
                xpad=0,
                tickvals=colorbar[option_dropdown]['tickvals'],
                ticktext=colorbar[option_dropdown]['ticktext'],
                tickfont=dict(color="#000000",
                              size=14),
                titlefont=dict(color="#000000",
                               size=16),
                ticksuffix=" hours",
                showticksuffix="all",
                thicknessmode="pixels",
            ),
        ),
    )]
    if dropdown_locations:
        mapbox_graph.append(
            # Plot of important locations on the map
            Scattermapbox(
                lat=[dropdown_locations[i]["lat"] for i in dropdown_locations],
                lon=[dropdown_locations[i]["lon"] for i in dropdown_locations],
                mode="markers",
                hoverinfo="text",
                text=[i for i in dropdown_locations],
                marker=dict(size=8, color="#000000"),
            )
        )

    return mapbox_graph
