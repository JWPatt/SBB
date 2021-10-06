# General
import pandas as pd
import time
import os

# Front end / plotting
import dash
from dash.dependencies import Input, Output
from plotly import graph_objs as go

# Project specific
import io_func
import app_frontend


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# List of selectable origin locations
dropdown_locations = app_frontend.get_dropdown_locations()

# List of selectable options and how they map to the correct columns in the database
options_list = ['Public Transport', 'Driving', 'Difference (public transport minus driving time)']
hovertext_cols, travel_time_cols = app_frontend.get_dropdown_maps(options_list)

# Colorbar for graphing (not very flexible)
colorbar = app_frontend.colorbar_config(4)

print(os.environ)
# Get tokens from the Heroku environment variable, else use a local file (not on github)
try:
    mgdb_url = os.environ.get('MONGODB_URI', None)
    print(os.environ.get('MONGODB_URI', None))
except:
    print("MongoDB url could not be found - environment variable 'MONGODB_URI' was not found")

try:
    print(os.environ.get('MAPBOX_PUBLIC', None))
    mapbox_access_token = os.environ.get('MAPBOX_PUBLIC', None)
except:
    print("Mapbox token could not be found - environment variable 'MAPBOX_PUBLIC' was not found")


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
    if not sbb_json:
        return go.Figure()

    sbb = pd.read_json(sbb_json)

    if display_times != [] or len(display_times) != 0:
        sbb_list = []
        display_times = [int(i) for i in display_times]
        for i in range(len(display_times)):
            sbb_list.append(sbb[(sbb[travel_time_cols[options_list[option_dropdown]]] <= display_times[i] * 3600) &
                                (sbb[travel_time_cols[options_list[option_dropdown]]] > (display_times[i] - 1) * 3600)])
        sbb = pd.concat(sbb_list)


    return go.Figure(
        data=app_frontend.get_mapbox_graph(sbb,
                                           hovertext_cols,
                                           options_list,
                                           option_dropdown,
                                           colorbar,
                                           travel_time_cols,
                                           # dropdown_locations     # Uncomment to add point at origins cities
                                           ),
        layout=app_frontend.get_mapbox_layout(mapbox_access_token),
    )


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=5000)
