import pandas as pd
import json
import urllib.request
import plotly
import plotly.graph_objs as go
import io_func


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

    # read data in from a csv
    # sbb = pd.read_csv(intermediate_data_name,names=['city', 'lat', 'lon', 'duration'])
    # sbb = sbb.round({'lat': 3, 'lon': 3})
    # sbb['hovertext'] = sbb['city'] + "<br>" +  sbb['duration'].apply(sec_to_hhmm)

    # read data in from a MongoDB
    mgdb = io_func.MongodbHandler.init_and_set_col("127.0.0.1:27017", "SBB_time_map", origin_details)
    sbb = pd.DataFrame(mgdb.get_data()).drop('_id',axis=1).rename(columns={'destination': 'city', 'travel_time': 'duration'})
    sbb = sbb.groupby(['city']).min().reset_index()
    sbb = sbb.round({'lat': 3, 'lon': 3})
    sbb['hovertext'] = sbb['city'] + "<br>" + sbb['duration'].apply(sec_to_hhmm)

    print(sbb)

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
                                  ),
                      height=800
                      )

    fig.show()

    # fig.write_html("example_results/zurich_summer_saturday_0700.html",include_mathjax = False)
    fig.write_html("templates/output_map.html", include_mathjax=False)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


if __name__ == "__main__":
    make_html_map('../example_results/Zurich_HB_7:00_2021-06-25.csv', ['Zurich HB', '2021-06-25', '7:00'])
