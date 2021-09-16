# General
import pandas as pd
import numpy as np
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


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# List of origin locations in Switzerland
dropdown_locations = core_func.get_dropdown_locations()
options_list = ['Public Transport', 'Driving', 'Difference (public transport minus driving time)']
hovertext_cols,travel_time_cols = core_func.get_dropdown_maps()

colorbar = core_func.colorbar_config()
#Currently these are not flexible
n_bins = 28
n_bins_diff = 24

# Get tokens from the Heroku environment variable, else use a local file (not on github)
mgdb_url = os.environ.get('MONGODB_URI', None)
if not mgdb_url: mgdb_url = pd.read_csv("io_func/secret_mgdb_pw.csv")
mapbox_access_token = os.environ.get('MAPBOX_PUBLIC', None)
if not mapbox_access_token: mapbox_access_token = pd.read_csv("io_func/secret_mapbox_pw.csv").columns[0]


# Layout of Dash App
# Note that a hidden div exists at the end to share data between callbacks
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.H2("Swiss Travel Time Map"),
                        html.P([
                            """This map shows every train, tram, and bus station in Switzerland, colored by the travel
                            time from the chosen origin city.""", html.Br(),html.Br(),
                            """Select a city of origin, a date of travel, and departure time. Filter the results by 
                            trip duration by selecting durations on the histogram."""
                        ]),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                # Dropdown for locations on map
                                dcc.Dropdown(
                                    id="location-dropdown",
                                    options=[
                                        {
                                            "label": n,
                                            "value": n
                                        }
                                        for n in dropdown_locations
                                    ],
                                    placeholder="Select a starting location",
                                    value='Zürich HB',
                                )
                            ],
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                # Dropdown for choosing which time to show
                                dcc.Dropdown(
                                    id="option-dropdown",
                                    options=[
                                        {
                                            "label": n,
                                            "value": i,
                                        }
                                        for i, n in enumerate(options_list)
                                    ],
                                    placeholder="Public Transport or Driving?",
                                    value=0,
                                )
                            ],
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                # Dropdown to select times
                                dcc.Dropdown(
                                    id="max-time-dropdown",
                                    options=[
                                        {
                                            "label": str(n) + ":00",
                                            "value": str(n),
                                        }
                                        for n in range(8)
                                    ],
                                    multi=True,
                                    placeholder="Select duration range",
                                ),
                            ],
                        ),
                        html.Div(
                            style={'display':'none'},
                            className="div-for-search-bar",
                            children=[
                                # Search bar to input origin city
                                dcc.Input(
                                    id="origin-city-search-bar",
                                    type="text",
                                    placeholder="Enter new origin",
                                ),

                            ],
                        ),
                        html.P(id="date-value"),
                        dcc.Markdown(
                            children=[
                                "Source: [search.ch](https://timetable.search.ch)"
                            ],
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Loading(
                            id="loading-graph",
                            type="default",
                            children=[html.Div(dcc.Graph(id="map-graph",
                                                         style={'height':'70vh'},
                                                         figure = core_func.blank_fig()),)],
                            style={'height':'70vh'}
                        ),

                        html.Div(
                            className="text-padding",
                            children=[
                                "Select any of the bars on the histogram to section data by time."
                            ],
                        ),

                        dcc.Loading(
                            id="loading-histogram",
                            type="default",
                            children=[html.Div(dcc.Graph(id="histogram",
                                                         style={'height':'27vh'},
                                                         figure = core_func.blank_fig()))],
                            style={'height':'30vh'}
                        ),
                    ],
                ),
            ],
        ),
        html.Div(id='update-signal', style={'display':'none'})
    ]
)


# Get data from MongoDB, process for use by plotly
def global_store(selectedData, selectedLocation, searchBar):
    if not selectedLocation:
        selectedLocation = 'Bern'

    if not searchBar:
        searchBar = None
    else:
        selectedLocation = searchBar

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
        Input("max-time-dropdown", "value"),
        Input("origin-city-search-bar", "value"),
    ],
)
def update_hidden_div(selectedLocation, selectedData, searchBar):
    sbb = global_store(selectedData, selectedLocation, searchBar)
    return sbb.to_json()


# Selected Data in the Histogram updates the Values in the Hours selection dropdown menu
@app.callback(
    Output("max-time-dropdown", "value"),
    [
        Input("histogram", "selectedData"),
        Input("histogram", "clickData")
    ],
)
def update_bar_selector(value, clickData):
    holder = []
    if clickData:
        holder.append(str(int(clickData["points"][0]["x"])+1))
    if value:
        for x in value["points"]:
            holder.append(str(int(x["x"])+1))
    return list(set(holder))


# Clear Selected Data if Click Data is used
@app.callback(Output("histogram", "selectedData"), [Input("histogram", "clickData")])
def update_selected_data(clickData):
    if clickData:
        return {"points": []}


# Update Histogram Figure based on Month, Day and Times Chosen
@app.callback(
    Output("histogram", "figure"),
    [Input("update-signal", "children"),
     Input("option-dropdown", "value")],
)
def update_histogram(sbb_json, option_dropdown):
    if sbb_json:
        sbb = pd.read_json(sbb_json)

        #hacky method to keep hsitogram color bins correct
        xVal = sbb[travel_time_cols[options_list[option_dropdown]]] / 3600
        if option_dropdown == 2:
            xVal = xVal.append(pd.Series([-1.499]))

        cmin = min(colorbar[option_dropdown]['intervals'])
        cmax = max(colorbar[option_dropdown]['intervals'])

        layout = go.Layout(
            bargap=0.01,
            bargroupgap=0,
            barmode="group",
            margin=go.layout.Margin(l=10, r=0, t=0, b=50),
            showlegend=False,
            plot_bgcolor="#323130",
            paper_bgcolor="#323130",
            # coloraxis_colorscale='RdBu',
            dragmode="select",
            font=dict(color="white"),
            xaxis=dict(
                range=[min(colorbar[option_dropdown]['intervals']), max(colorbar[option_dropdown]['intervals'])],
                showgrid=False,
                nticks=9,
                fixedrange=True,
                ticksuffix=":00",
            ),
            yaxis=dict(
                # range=[0, max(yVal) + max(yVal) / 4],
                showticklabels=False,
                showgrid=False,
                fixedrange=True,
                rangemode="nonnegative",
                zeroline=False,
            ),
        )
    else:
        xVal = []
        layout = go.Layout()

    return go.Figure(
        data=[
            go.Histogram(x=xVal,
                         marker=dict(
                             color=colorbar[option_dropdown]['colors_histogram'],
                             cmax=cmax,
                             cmin=cmin,
                         ),
                         hoverinfo="x",
                         xbins=dict(
                             start=min(colorbar[option_dropdown]['intervals']) if option_dropdown < 3 else -1.5 ,
                             end=max(colorbar[option_dropdown]['intervals']) if option_dropdown < 3 else -1.5 ,
                             size=(max(colorbar[option_dropdown]['intervals']) - min(colorbar[option_dropdown]['intervals']))/(n_bins if option_dropdown < 2 else n_bins_diff)
                            ),
                         ),
        ],
        layout=layout,
    )


# Update Map Graph based on date-dropdown, selected data on histogram and location dropdown
@app.callback(
    Output("map-graph", "figure"),
    [Input("update-signal", "children"),
     Input("max-time-dropdown", "value"),
     Input("option-dropdown", "value"),]
)
def update_graph(sbb_json, display_times, option_dropdown):
    t_init = time.time()
    if not sbb_json:
        return go.Figure()

    sbb = pd.read_json(sbb_json)
    zoom = 6.7
    lat_default = 46.83
    lon_default = 7.93
    bearing = 0

    if display_times != [] or len(display_times) != 0:
        sbb_list = []
        display_times = [int(i) for i in display_times]
        for i in range(len(display_times)):
            sbb_list.append(sbb[(sbb[travel_time_cols[options_list[option_dropdown]]] <= display_times[i] * 60 * 60) & (sbb[travel_time_cols[options_list[option_dropdown]]] > (display_times[i] - 1) * 60 * 60)])
        sbb = pd.concat(sbb_list)

    figure_settings = {}
    cmin = min(colorbar[option_dropdown]['intervals'])*3600
    cmax = max(colorbar[option_dropdown]['intervals'])*3600

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
        layout=Layout(
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
    app.run_server(debug=False, host='0.0.0.0', port=5001)
