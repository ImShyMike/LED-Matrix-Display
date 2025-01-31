"""Example server for the display. (requires Flask and psutil)"""

import flask
import psutil

app = flask.Flask(__name__)


@app.route("/data")
def data():
    """Return data."""
    return {
        "CPU": round(psutil.cpu_percent()),
        "RAM": round(psutil.virtual_memory().percent),
        "Temp": round(psutil.sensors_temperatures()["cpu_thermal"][0].current),
    }


if __name__ == "__main__":
    app.run()
