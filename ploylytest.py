import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np

from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
from flask_caching import Cache


import io_func
import core_func
import time
import os


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
# CACHE_CONFIG = {
#     'CACHE_TYPE':'redis',
#     'CACHE_REDIS_URL': os.environ.get('REDIS_URL','redis://localhost:6379')
# }
CACHE_CONFIG = {
    'CACHE_TYPE':'filesystem',
    'CACHE_DIR': 'cache-directory'
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)
# server = app.server


# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

# Dictionary of important locations in New York
list_of_locations = {
    "Zurich HB": {"lat": 47.3779, "lon": 8.5403},
    "Bern": {"lat": 46.9490, "lon": 7.4385},
    "Geneva": {"lat": 46.2044, "lon": 6.1413},
    "Lugano": {"lat": 46.0037, "lon": 8.9511},
    "Basel": {"lat": 47.5596, "lon": 7.5886},
    "Lausanne": {"lat": 46.5197, "lon": 6.6323}
}

pw = pd.read_csv("io_func/secret_mgdb_pw.csv")
mgdb_url = "mongodb+srv://admin_patty:" + pw.columns.to_list()[0] + "@clusteruetliberg.erwru.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
t_init = time.time()

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
                        html.Img(
                            className="logo", src=app.get_asset_url("dash-logo-new.png")
                        ),
                        html.H2("SBB Travel Time Map"),
                        html.P(
                            """Select a city of origin, a date of travel, and departure time. Filter the results by 
                            trip duration by selecting durations on the histogram."""
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                # Dropdown for locations on map
                                dcc.Dropdown(
                                    id="location-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in list_of_locations
                                    ],
                                    placeholder="Select a starting location",
                                )
                            ],
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-dropdown",
                                    min_date_allowed=dt(2021, 1, 1),
                                    max_date_allowed=dt(2021, 12, 31),
                                    initial_visible_month=dt(2021, 6, 26),
                                    date=dt(2021, 6, 26).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        # Change to side-by-side for mobile layout
                        # html.Div(
                        #     className="row",
                        #     children=[

                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                # Dropdown for locations on map
                                dcc.Dropdown(
                                    id="starttime-dropdown",
                                    options=[
                                        {
                                            "label": str(n) + ":00",
                                            "value": str(n) + ":00",
                                        }
                                        for n in range(24)
                                    ],
                                    placeholder="Select a departure time",
                                    value='7:00',
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
                                    placeholder="Select maximum duration",
                                )
                            ],
                        ),
                        #     ],
                        # ),
                        html.P(id="date-value"),
                        dcc.Markdown(
                            children=[
                                "Source: [search.ch](https://timetable.search.ch)"
                            ]
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="map-graph", style={'height':'70vh'}),
                        html.Div(
                            className="text-padding",
                            children=[
                                "Select any of the bars on the histogram to section data by time."
                            ],
                        ),
                        dcc.Graph(id="histogram"),
                    ],
                ),
            ],
        ),
        html.Div(id='update-signal', style={'display':'none'})
    ]
)

@cache.memoize()
def global_store(datePicked, selectedData, selectedLocation, starttime):
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")

    if date_picked.weekday() > 4:
        startdate = '2021-06-26'
    else:
        startdate = '2021-06-25'

    if not selectedLocation:
        selectedLocation = 'Bern'
    if not starttime:
        starttime = '8:00'

    origin_details = [selectedLocation, startdate, starttime]
    print (origin_details)
    mgdb = io_func.MongodbHandler.init_and_set_col(mgdb_url, "SBB_time_map", origin_details)

    sbb = pd.DataFrame(mgdb.get_data_list()).drop('_id', axis=1).rename(
        columns={'destination': 'city', 'travel_time': 'duration'})

    # cap the maximum duration which gets colored to maintain appropriate colors in majority of points
    # cap_max = 60 * 60 * 6
    # sbb.loc[sbb['duration'] > cap_max, 'duration'] = cap_max

    return sbb


@app.callback(
    Output("update-signal", "children"),
    [
        Input("date-dropdown", "date"),
        Input("starttime-dropdown", "value"),
        Input("location-dropdown", "value"),
        Input("max-time-dropdown", "value"),
    ],
)
def update_hidden_div(datePicked, starttime, selectedLocation, selectedData):
    t_init = time.time()
    print('starting sbb: ', time.time() - t_init)
    sbb = global_store(datePicked, selectedData, selectedLocation, starttime)
    print('returning sbb: ', time.time() - t_init)
    return sbb.to_json()


# Selected Data in the Histogram updates the Values in the Hours selection dropdown menu
@app.callback(
    Output("max-time-dropdown", "value"),
    [Input("histogram", "selectedData"), Input("histogram", "clickData")],
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
    [Input("update-signal", "children")],
)
def update_histogram(sbb_json):

    print('updating histogram: ', time.time() - t_init)
    if sbb_json:
        sbb = pd.read_json(sbb_json)

        xVal = sbb['duration']/60/60

        layout = go.Layout(
            bargap=0.01,
            bargroupgap=0,
            barmode="group",
            margin=go.layout.Margin(l=10, r=0, t=0, b=50),
            showlegend=False,
            plot_bgcolor="#323130",
            paper_bgcolor="#323130",
            coloraxis_colorscale='algae_r',
            dragmode="select",
            font=dict(color="white"),
            xaxis=dict(
                range=[-0.5, 7.5],
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
            # annotations=[
            #     dict(
            #         x=xi,
            #         y=yi,
            #         text=str(yi),
            #         xanchor="center",
            #         yanchor="bottom",
            #         showarrow=False,
            #         font=dict(color="white"),
            #     )
            #     for xi, yi in zip(xVal, yVal)
            # ],
        )
    else:
        xVal = []
        layout = go.Layout()

    print('returning histogram: ', time.time() - t_init)
    return go.Figure(
        data=[
            go.Histogram(x=xVal,
                         # marker=dict(color=colorVal),
                         hoverinfo="x",
                         xbins=dict(
                             start=0,
                             end=24,
                             size=1.0
                            ),
                         ),
            # go.Scatter(
            #     opacity=0,
            #     x=xVal,
            #     y=yVal / 2,
            #     hoverinfo="none",
            #     mode="markers",
            #     marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
            #     visible=True,
            # ),
        ],
        layout=layout,
    )


# Update Map Graph based on date-dropdown, selected data on histogram and location dropdown
@app.callback(
    Output("map-graph", "figure"),
    [Input("update-signal", "children"),
     Input("max-time-dropdown", "value")]
)
def update_graph(sbb_json, display_times):

    print('updating graph: ', time.time() - t_init)
    if not sbb_json:
        return go.Figure()
    sbb = pd.read_json(sbb_json)
    zoom = 6.75
    lat_default = 46.8181877
    lon_default = 8.2275124
    bearing = 0

    if display_times != [] or len(display_times) != 0:
        sbb_list = []
        display_times = [int(i) for i in display_times]
        for i in range(len(display_times)):
            sbb_list.append(sbb[(sbb['duration'] <= display_times[i] * 60 * 60 ) & (sbb['duration'] >= (display_times[i] - 1) * 60 * 60)])
            # sbb_list[i] = sbb_list[i][sbb_list[i]['duration'] >= (i - 1) * 60 * 60]
        sbb = sbb_list

    print('returning graph: ', time.time() - t_init)
    return go.Figure(
        data=[
            # Data for all rides based on date and time
            Scattermapbox(
                lat=sbb["lat"],
                lon=sbb["lon"],
                mode="markers",
                hoverinfo='text',
                hovertext=sbb['hovertext'],
                text=sbb['city'],
                marker=dict(
                    showscale=True,
                    color=sbb['duration'],
                    opacity=0.75,
                    size=7.5,
                    # colorscale=[
                    #     [0, "#F4EC15"],
                    #     [0.04167, "#DAF017"],
                    #     [0.0833, "#BBEC19"],
                    #     [0.125, "#9DE81B"],
                    #     [0.1667, "#80E41D"],
                    #     [0.2083, "#66E01F"],
                    #     [0.25, "#4CDC20"],
                    #     [0.292, "#34D822"],
                    #     [0.333, "#24D249"],
                    #     [0.375, "#25D042"],
                    #     [0.4167, "#26CC58"],
                    #     [0.4583, "#28C86D"],
                    #     [0.50, "#29C481"],
                    #     [0.54167, "#2AC093"],
                    #     [0.5833, "#2BBCA4"],
                    #     [1.0, "#613099"],
                    # ],
                    colorbar=dict(
                        title="Travel Time (hours)",
                        x=0.93,
                        xpad=0,
                        nticks=6,
                        tickfont=dict(color="#d8d8d8"),
                        titlefont=dict(color="#d8d8d8"),
                        thicknessmode="pixels",
                    ),
                ),
            ),
            # Plot of important locations on the map
            Scattermapbox(
                lat=[list_of_locations[i]["lat"] for i in list_of_locations],
                lon=[list_of_locations[i]["lon"] for i in list_of_locations],
                mode="markers",
                hoverinfo="text",
                text=[i for i in list_of_locations],
                marker=dict(size=8, color="#ffa0a0"),
            ),
        ],
        layout=Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=35, t=0, b=0),
            showlegend=False,
            coloraxis_colorscale='algae_r',
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
    app.run_server(debug=True)