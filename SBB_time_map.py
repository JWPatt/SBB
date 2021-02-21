import io_func
import core_func
from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def home():
    # Enter city name with or without special characters (probably safer without)
    # Enter time in HH:MM format (e.g. '13:10')
    # Enter date in YYYY-MM-DD format (e.g. '2021-11-22')
    origin_city = ['Zurich HB', 'Bern', 'Geneva']
    origin_time = ['7:00', '7:00', '7:00']
    origin_date = ['2021-06-25', '2021-06-25', '2021-06-25']
    origin_details = [[origin_city[i], origin_time[i], origin_date[i]] for i in range(3)]
    try:
        for i in origin_details[:1]:
            success = core_func.main(i)
            if success:
                data_csv = io_func.database_loc('output_csvs/', i)
                plotly_map = core_func.make_html_map(data_csv, i)

                # return render_template("output_map.html")  # stand-alone, static plotly map
                return render_template("index.html", graphJSON=plotly_map)  # via json-ified plotly
    except KeyboardInterrupt or EOFError:
        print("Killed by user.")
    except:
        raise


if __name__ == "__main__":
    app.run(debug=True)
