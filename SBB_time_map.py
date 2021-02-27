import io_func
import core_func
from flask import Flask, render_template
import flask
from pymongo import MongoClient
from wtforms import Form, BooleanField, StringField, validators, SelectField


app = Flask(__name__)


# @app.route("/drop", methods=['GET', 'POST'])
# def dropdown():
#     if flask.request.method == 'POST':
#         print( "good")


@app.route("/", methods=['GET'])
def dropdown2():
    print('print')
    mgdb = io_func.MongodbHandler("127.0.0.1:27017", "SBB_time_map")
    return render_template('index.html', origin_cities=mgdb.collections)


@app.route("/drop", methods=['POST'])
def home():
    mgdb = io_func.MongodbHandler("127.0.0.1:27017", "SBB_time_map")
    # Enter city name with or without special characters (probably safer without)
    # Enter time in HH:MM format (e.g. '13:10')
    # Enter date in YYYY-MM-DD format (e.g. '2021-11-22')

    origin_city = ['Zurich HB', 'Bern', 'Geneva']
    origin_date = ['2021-06-25', '2021-06-25', '2021-06-25']
    origin_time = ['7:00', '7:00', '7:00']
    origin_details = [[origin_city[i], origin_date[i], origin_time[i]] for i in range(3)]

    origin_details = flask.request.form.get("origin_cities").split(".")
    origin_details[0] = origin_details[0].replace("_"," ")
    origin_details[1] = origin_details[1].replace("_","-")
    origin_details[2] = origin_details[2].replace("_",":")
    print(origin_details)
    try:
        success = core_func.primary(origin_details)
        if success:
            data_csv = io_func.database_loc('output_csvs/', origin_details)
            plotly_map = core_func.make_html_map(data_csv, origin_details)

            # return render_template("output_map.html")  # stand-alone, static plotly map
        return render_template("index.html", origin_cities=mgdb.collections, graphJSON=plotly_map)  # via json-ified plotly
    except KeyboardInterrupt or EOFError:
        print("Killed by user.")
    except:
        raise








if __name__ == "__main__":
    app.run(debug=True)
