# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/<start_date><br/>"
        f"/api/v1.0/start_end_date/<start>/<end><br/>"
    )

# app routing for precipitation for the past 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    cutoff_date = '2016-08-23'
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > cutoff_date).all()
    session.close()

    precip_data = []
    for date, prcp in results:
        precip_data.append({"date": date, "prcp": prcp})

    return jsonify(precip_data)

# app routing for station list
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Measurement.station).distinct().all()
    session.close()

    station_data = [{"station name": station[0]} for station in results]
    return jsonify(station_data)

# app routing for observed temperatures for the past 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    cutoff_date_12month = '2016-08-23'
    results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.station == 'USC00519281') & (Measurement.date > cutoff_date_12month)).all()
    session.close()

    tobs_data = [{"Date": date, "Observed Temperature": tobs} for date, tobs in results]
    return jsonify(tobs_data)

# app routing for min, max, avg temp for a given start date
@app.route("/api/v1.0/start/<start_date>")
def temps_start(start_date):
    session = Session(engine)
    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    session.close()

    temp_data = []
    if results:
        temp_dict = {
            "Average": results[0][0],
            "Minimum": results[0][1],
            "Maximum": results[0][2]
        }
        temp_data.append(temp_dict)

    return jsonify(temp_data)

# app routing for min, max, avg temp for a given start and end date
@app.route("/api/v1.0/start_end_date/<start>/<end>")
def temps_start_end(start, end):
    session = Session(engine)
    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).filter((Measurement.date >= start) & (Measurement.date <= end)).all()
    session.close()

    temp_data = []
    if results:
        temp_dict = {
            "Average": results[0][0],
            "Minimum": results[0][1],
            "Maximum": results[0][2]
        }
        temp_data.append(temp_dict)

    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)