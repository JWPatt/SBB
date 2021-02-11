import numpy as np
import pandas as pd
import json
import urllib.request
import plotly.graph_objs as go


def sec_to_hhmm(seconds):
    hours = seconds//3600
    minutes = (seconds-3600*hours)//60
    return str(hours) + ":" + str(minutes).zfill(2)


def read_geojson(url):
    with urllib.request.urlopen(url) as url:
        jdata = json.loads(url.read().decode())
    return jdata


def make_html_map(path_to_data, origin_details):
    intermediate_data_name = path_to_data

    sbb = pd.read_csv(intermediate_data_name,names=['city', 'lat', 'lon', 'duration'])
    sbb = sbb.round({'lat': 3, 'lon': 3})
    # sbb['hovertext'] = [sbb['city'], sbb['duration'].apply(sec_to_hhmm)]
    sbb['hovertext'] = sbb['city'] + "<br>" +  sbb['duration'].apply(sec_to_hhmm)

    # cap the maximum duration which gets colored to maintain appropriate colors in majority of points
    cap_max = 60*60*6
    sbb.loc[sbb['duration'] > cap_max,'duration'] = cap_max



    # swiss_url = 'https://raw.githubusercontent.com/empet/Datasets/master/swiss-cantons.geojson'
    # jdata = read_geojson(swiss_url)
    #
    # data_url = "https://raw.githubusercontent.com/empet/Datasets/master/Swiss-synthetic-data.csv"
    # df = pd.read_csv(data_url)
    # print(df.head())
    # mycustomdata = np.stack((df['canton-name'], df['2018']), axis=-1)
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
        lon=sbb['lon'],
        lat=sbb['lat'],
        mode='markers',
        marker_color=sbb['duration'],
        marker_size=10,
        text=sbb['city'],
        hovertext=sbb['hovertext'],
        hoverinfo='text',
    ))

    fig.update_layout(title_text='SBB Journey Lengths, from %s on Saturdays at %s on %s' % (origin_details[0], origin_details[1], origin_details[2]),
                      title_x=0.5,
                      coloraxis_colorscale='algae_r',
                      mapbox=dict(style='carto-positron',
                                  zoom=6.75,
                                  center={"lat": 46.8181877, "lon": 8.2275124},
                                  )
                      )

    fig.show()

    # fig.write_html("example_results/zurich_summer_saturday_0700.html",include_mathjax = False)


if __name__ == "__main__":
    make_html_map('example_results/main_table.csv',['Zurich HB','7:00','2021-06-25'])
