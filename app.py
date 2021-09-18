# General
import pandas as pd
import time
import os

# Front end / plotting
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from plotly import graph_objs as go
from plotly.graph_objs import *

# Project specific
import io_func
import core_func
import app_frontend


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# List of origin locations in Switzerland
dropdown_locations = app_frontend.get_dropdown_locations()
options_list = ['Public Transport', 'Driving', 'Difference (public transport minus driving time)']
hovertext_cols,travel_time_cols = app_frontend.get_dropdown_maps()

colorbar = app_frontend.colorbar_config()

# Get tokens from the Heroku environment variable, else use a local file (not on github)
mgdb_url = os.environ.get('MONGODB_URI', None)
if not mgdb_url: mgdb_url = pd.read_csv("io_func/secret_mgdb_pw.csv")
mapbox_access_token = os.environ.get('MAPBOX_PUBLIC', None)
if not mapbox_access_token: mapbox_access_token = pd.read_csv("io_func/secret_mapbox_pw.csv").columns[0]


# Layout of Dash App
app.layout = app_frontend.get_page_layout(dropdown_locations, options_list)


# Get data from MongoDB, process for use by plotly
def global_store(selectedLocation):
    if not selectedLocation:
        selectedLocation = 'Bern'

    mgdb = io_func.MongodbHandler.init_and_set_col(mgdb_url, "SBB_time_map_test2", selectedLocation)

    sbb = pd.DataFrame(mgdb.get_data_list()).drop('_id', axis=1)
    sbb['drive_minus_train'] = -sbb['drive_minus_train']
    return sbb


# Getting the data is expensive; get it once and store the data in hidden div for use by other callbacks
# Outputs to "update-signal", signalling the plots to update using the new data.
@app.callback(
    Output("update-signal", "children"),
    [
        Input("location-dropdown", "value"),
    ],
)
def update_hidden_div(selected_location):
    sbb = global_store(selected_location)
    return sbb.to_json()


# Selected Data in the Histogram updates the Values in the Hours selection dropdown menu
@app.callback(
    Output("max-time-dropdown", "value"),
    [
        Input("histogram", "selectedData"),
        Input("histogram", "clickData")
    ],
)
def update_bar_selector(value, selected_times):
    holder = []
    if selected_times:
        holder.append(str(int(selected_times["points"][0]["x"]) + 1))
    if value:
        for x in value["points"]:
            holder.append(str(int(x["x"])+1))
    return list(set(holder))


# Clear Selected Data if Click Data is used
@app.callback(Output("histogram", "selectedData"),
              [
                  Input("histogram", "clickData")
              ],
)
def update_selected_data(selected_times):
    if selected_times:
        return {"points": []}


# Update Histogram Figure based on Month, Day and Times Chosen
@app.callback(
    Output("histogram", "figure"),
    [
        Input("update-signal", "children"),
        Input("option-dropdown", "value"),
    ],
)
def update_histogram(sbb_json, option_dropdown):
    if sbb_json:
        sbb = pd.read_json(sbb_json)

        # Plotly histograms only generate bins within the range of the data given
        # Therefore, to set a consistent color scheme, you need to fabricate a bin near the minimum
        # Only needed for the difference map, since the minimum bin with the data
        hist_x_vals = sbb[travel_time_cols[options_list[option_dropdown]]] / 3600
        if option_dropdown == 2:
            hist_x_vals = hist_x_vals.append(pd.Series([-1.499]))

    else:
        hist_x_vals = []
        hist_layout = go.Layout()


    return go.Figure(
        data=app_frontend.get_hist_graph(hist_x_vals, colorbar, option_dropdown),
        layout=app_frontend.get_hist_layout(colorbar, option_dropdown),
    )


# Update Map Graph based on date-dropdown, selected data on histogram and location dropdown
@app.callback(
    Output("map-graph", "figure"),
    [
        Input("update-signal", "children"),
        Input("max-time-dropdown", "value"),
        Input("option-dropdown", "value"),
    ]
)
def update_graph(sbb_json, display_times, option_dropdown):
    t_init = time.time()
    if not sbb_json:
        return go.Figure()

    sbb = pd.read_json(sbb_json)

    if display_times != [] or len(display_times) != 0:
        sbb_list = []
        display_times = [int(i) for i in display_times]
        for i in range(len(display_times)):
            sbb_list.append(sbb[(sbb[travel_time_cols[options_list[option_dropdown]]] <= display_times[i] * 60 * 60) & (sbb[travel_time_cols[options_list[option_dropdown]]] > (display_times[i] - 1) * 60 * 60)])
        sbb = pd.concat(sbb_list)

    cmin = min(colorbar[option_dropdown]['intervals'])*3600
    cmax = max(colorbar[option_dropdown]['intervals'])*3600

    zoom = 6.7
    lat_default = 46.83
    lon_default = 7.93
    bearing = 0

    return go.Figure(
        data=[
            # Data for all rides based on date and time
            Scattermapbox(
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
            ),
            # Plot of important locations on the map
            # Scattermapbox(
            #     lat=[dropdown_locations[i]["lat"] for i in dropdown_locations],
            #     lon=[dropdown_locations[i]["lon"] for i in dropdown_locations],
            #     mode="markers",
            #     hoverinfo="text",
            #     text=[i for i in dropdown_locations],
            #     marker=dict(size=8, color="#ffa0a0"),
            # ),
        ],
        # layout=app_frontend.get_mapbox_layout(mapbox_access_token),
        layout=go.Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=35, t=0, b=0),
            showlegend=False,
            # coloraxis_colorscale='algae_r',
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=lat_default, lon=lon_default),  # 40.7272  # -73.991251
                style="carto-positron",
                bearing=bearing,
                zoom=zoom,
            ),
            updatemenus=[
                dict(
                    buttons=(
                        [
                            dict(
                                args=[
                                    {
                                        "mapbox.zoom": zoom,
                                        "mapbox.center.lon": lon_default,
                                        "mapbox.center.lat": lat_default,
                                        "mapbox.bearing": 0,
                                        "mapbox.style": "carto-positron",
                                    }
                                ],
                                label="Reset Zoom",
                                method="relayout",
                            )
                        ]
                    ),
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
        ),
    )


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=5000)
