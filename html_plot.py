import json
import matplotlib.pyplot as plt
import numpy
import datetime
import time
import pandas as pd
from read_in_csv import *
import numpy as np
import json
import urllib.request
import plotly.graph_objs as go

# with open('saved_sbb_table.txt', 'r') as file:
#     sbb_data = json.load(file)

intermediate_data_name = 'main_table.csv'

sbb_data = csv_to_dict(intermediate_data_name)
city = []
lat_data = []
lon_data = []
duration = []
for key in sbb_data:
    if sbb_data[key] is not None:
        city.append(key)
        lat_data.append(sbb_data[key][0])
        lon_data.append(sbb_data[key][1])
        duration.append(sbb_data[key][2])
        # duration.append(
        #     sum(x * int(t) for x, t in zip([3600, 60, 1], (sbb_data[key][2].replace('00d', '')).split(":")))
        # )
sbb = pd.DataFrame({'city':city,
                    'lat':lat_data,
                   'lon':lon_data,
                   'duration':duration})
print(sbb.iloc[sbb['duration'].idxmax()])

# print('does {} work?'.format(sbb['city']))

# cap_max = int(input('Current maximum is ' + str(max(duration)) + '. Cap maximum at: '))
cap_max = 60*60*8
sbb.loc[sbb['duration'] > cap_max,'duration'] = cap_max


def read_geojson(url):
    with urllib.request.urlopen(url) as url:
        jdata = json.loads(url.read().decode())
    return jdata

swiss_url = 'https://raw.githubusercontent.com/empet/Datasets/master/swiss-cantons.geojson'
jdata = read_geojson(swiss_url)
# print(jdata['features'][0].keys())
# print(jdata['features'][0]['properties'])
import pandas as pd

data_url = "https://raw.githubusercontent.com/empet/Datasets/master/Swiss-synthetic-data.csv"
df = pd.read_csv(data_url)
print(df.head())
mycustomdata = np.stack((df['canton-name'], df['2018']), axis=-1)
title = 'Swiss Canton Choroplethmapbox'

fig = go.Figure()
# fig.add_trace(go.Choroplethmapbox(geojson=jdata,
#                                     locations=df['canton-id'],
#                                     z=df['2018'],
#                                     featureidkey='properties.id',
#                                     coloraxis="coloraxis",
#                                     customdata=mycustomdata,
#                                     # hovertemplate='Canton: %{customdata[0]}' + '<br>2018: %{customdata[1]}%<extra></extra>',
#                                     marker_line_width=1))

fig.add_trace(go.Scattermapbox(      # Scattermapbox on tiles, scattergeo on outline maps
        lon = sbb['lon'],
        lat = sbb['lat'],
        mode = 'markers',
        marker_color = sbb['duration'],
        marker_size = 10,
        text=sbb['city'],
    # dest = sbb['city'],
hovertemplate =
    '<b>%{text}</b>'+
    '<br>%{marker_color} hours<br>'
    # text = ['Custom text {}'.format(i + 1) for i in range(5)]
        ))

# fig.add_trace(go.Scattergeo(      # choropleth on tiles, scattergeo on outline maps
#         lon = sbb['lon'],
#         lat = sbb['lat'],
#         mode = 'markers',
#         marker_color = sbb['duration'],
#         ))

fig.update_layout(title_text=title,
                  title_x=0.5,
                  coloraxis_colorscale='algae_r',
                  mapbox=dict(style='carto-positron',
                              zoom=6.5,
                              center={"lat": 46.8181877, "lon": 8.2275124},
                              ));



fig.show()