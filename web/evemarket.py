#!/usr/bin/env python
import sys
sys.path.append("../lib/")
import evemarket_lib
from flask import Flask, render_template, jsonify
application = Flask(__name__, static_folder='../static/', static_url_path="/")

@application.route("/trade/station/<stationid>")
def index(stationid):
    return render_template("index.html", trades=str(evemarket_lib.get_station_trades(stationid)))
    #return evemarket_lib.get_station_trades(stationid)

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
