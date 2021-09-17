from plotly import graph_objs as go


def get_hist_layout(colorbar, option_dropdown):
    hist_layout = go.Layout(
            bargap=0.01,
            bargroupgap=0,
            barmode="group",
            margin=go.layout.Margin(l=10, r=0, t=0, b=50),
            showlegend=False,
            plot_bgcolor="#323130",
            paper_bgcolor="#323130",
            dragmode="select",
            font=dict(color="white"),
            xaxis=dict(
                range=[min(colorbar[option_dropdown]['intervals']),
                       max(colorbar[option_dropdown]['intervals'])],
                showgrid=False,
                nticks=9,
                fixedrange=True,
                ticksuffix=":00",
            ),
            yaxis=dict(
                showticklabels=False,
                showgrid=False,
                fixedrange=True,
                rangemode="nonnegative",
                zeroline=False,
            ),
        )
    return hist_layout


def get_mapbox_layout(mapbox_access_token):
    zoom = 6.7
    lat_default = 46.83
    lon_default = 7.93
    bearing = 0

    return go.Layout(
            autosize=True,
            # margin=go.layout.Margin(l=0, r=35, t=0, b=0),
            margin={"l": 0, "r": 35, "t": 0, "b": 0},
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
