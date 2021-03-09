import io_func
import core_func
from flask import Flask, render_template
import pandas as pd
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
    pw = pd.read_csv("../io_func/secret_mgdb_pw.csv")
    mgdb = io_func.MongodbHandler("mongodb+srv://admin_patty:" + pw.columns.to_list()[
        0] + "@cluster0.erwru.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", "SBB_time_map")

    # mgdb = io_func.MongodbHandler("127.0.0.1:27017", "SBB_time_map")
    return render_template('index.html', origin_cities=mgdb.collections)


@app.route("/drop", methods=['POST'])
def home():
    pw = pd.read_csv("../io_func/secret_mgdb_pw.csv")
    mgdb = io_func.MongodbHandler("mongodb+srv://admin_patty:" + pw.columns.to_list()[
        0] + "@cluster0.erwru.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", "SBB_time_map")

    # mgdb = io_func.MongodbHandler("127.0.0.1:27017", "SBB_time_map")
    # Enter city name with or without special characters (probably safer without)
    # Enter time in HH:MM format (e.g. '13:10')
    # Enter date in YYYY-MM-DD format (e.g. '2021-11-22')
    origin_city = ['Zurich HB']
    origin_date = ['2021-06-25']
    origin_time = ['6:00']
    # origin_city = ['Zurich HB', 'Bern', 'Geneva', 'Lugano', 'Basel', 'Lausanne']
    # origin_date = ['2021-06-25' ,'2021-06-26']
    # origin_time = ['6:00','7:00', '8:00', '9:00']
    origin_details_list = []
    for city in origin_city:
        for date in origin_date:
            for time in origin_time:
                origin_details_list.append([city, date, time])

    # origin_details_list = [[origin_city[i], origin_date[i], origin_time[i]] for i in range(3)]
    # origin_details_list = origin_details[0]

    # origin_details = flask.request.form.get("origin_cities").split(".")
    # origin_details[0] = origin_details[0].replace("_"," ")
    # origin_details[1] = origin_details[1].replace("_","-")
    # origin_details[2] = origin_details[2].replace("_",":")

    for origin_details in origin_details_list:
        print(origin_details)
        try:
            mgdb.set_col(origin_details)
            success = core_func.primary(origin_details, mgdb)
            if success:
                data_csv = io_func.database_loc('output_csvs/', origin_details)
                plotly_map = core_func.make_html_map(data_csv, origin_details)

                # return render_template("output_map.html")  # stand-alone, static plotly map
            # return render_template("index.html", origin_cities=mgdb.collections, graphJSON=plotly_map)  # via json-ified plotly
        except KeyboardInterrupt or EOFError:
            print("Killed by user.")
        except:
            raise








if __name__ == "__main__":
    app.run(debug=True)
