import dash_core_components as dcc
import dash_html_components as html
import core_func


def get_page_layout(dropdown_locations, options_list):
    page_layout = html.Div(
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
                                time from the chosen origin city.""", html.Br(), html.Br(),
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
                                style={'display': 'none'},
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
                                                             style={'height': '70vh'},
                                                             figure=core_func.blank_fig()),)],
                                style={'height': '70vh'}
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
                                                             style={'height': '27vh'},
                                                             figure=core_func.blank_fig()))],
                                style={'height': '30vh'}
                            ),
                        ],
                    ),
                ],
            ),

            # hidden div exists to share data between callbacks
            html.Div(id='update-signal', style={'display': 'none'})
        ]
    )

    return page_layout
