# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
station = base.classes.station
measurement = base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def starting():
    return (
        f"Climate Analysis API for Hawaii.<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start] (date format: YYYY-MM-DD)<br/>"
        f"/api/v1.0/[start]/[end] (date format: YYYY-MM-DD/YYYY-MM-DD)"

    )

@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)
    
    lastest_date = session.query(func.max(measurement.date)).scalar()
    last_year_date = dt.datetime.strptime(lastest_date, '%Y-%m-%d') - dt.timedelta(days=365)

    results= session.query(measurement.date, measurement.prcp).filter(measurement.date >= last_year_date).order_by(measurement.date.desc()).all()

    precipitation = dict(results)

    print(f"Results for Precipitation - {precipitation}")
    print("Out of Precipitation section.")
    return jsonify(precipitation) 



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    selection = [station.station    , station.name, station.latitude, station.longitude, station.elevation]
    query_result = session.query(*selection).all()
    session.close()

    stations = []
    for station_id,name,lat,lng,elev in query_result:
        station_dict = {}
        station_dict["Station"] = station_id
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lng"] = lng
        station_dict["Elevation"] = elev
        stations.append(station_dict)

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    lastest_date = session.query(func.max(measurement.date)).scalar()
    last_year_date = dt.datetime.strptime(lastest_date, '%Y-%m-%d') - dt.timedelta(days=365)

    station_activity = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active = station_activity[0][0]

    query_result = session.query(measurement.date, measurement.tobs).filter(measurement.station==most_active).filter(measurement.date>=last_year_date).all()

    tob_obs = []
    for date, tobs in query_result:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tob_obs.append(tobs_dict)

    return jsonify(tob_obs)


@app.route("/api/v1.0/<start>")

def get_temps_start(start):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)


@app.route("/api/v1.0/<start>/<end>")
def get_temps_start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)