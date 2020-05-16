import numpy as np
import datetime as dt

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
Base.prepare(engine, reflect = True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# inspector = inspect(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Query the date and precipitation
    results = session.query (Measurement.date, Measurement.prcp).all()
    session.close()

    # Create a precipitation query: date as index and prcp as value
    precipitation_list = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_list.append(precipitation_dict)
    
    return jsonify(precipitation_list)

# Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)

    # Query station
    results = session.query(Station.station, Station.name).all()
    session.close()

    return jsonify(results)

# Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")

def tobs():
    session = Session(engine)

    #query dates and temp observations
    # results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>= '2016-08-23').all()
    results = session.query(Measurement.date, Measurement.tobs, Measurement.station).filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.station == 'USC00519281').all()


    tobs_list = []
    for date, tobs, station in results:
        dates_temp_dict = {}
        dates_temp_dict["date"] = date
        dates_temp_dict["tobs"] = tobs
        dates_temp_dict["station"] = station
        tobs_list.append(dates_temp_dict)
    return jsonify(tobs_list)

"""Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    #change start date to datetime
    # start_date = dt.datetime.strftime('%Y-%m-%d')
    # measurement.date = dt.date  
    results = session.query(Measurement.date), func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs). filter(Measurement.date>= start_date).all()
    session.close()
    start_list = []
    for date, min, avg, max in results:
        start_dict = {}
        start_dict["date"] = start_date
        start_dict["TMIN"] = min
        start_dict["TAVG"] = avg
        start_dict["TMAX"] = max
        start_list.append(start_dict)
    return jsonify(start_list)
@app.route('/api/v1.0/<start>/<end>')
def end_date(start,end):
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    end_list = []

    for date, min, avg, max in results:
        end_dict = {}
        end_dict["date"] = date
        end_dict["TMIN"] = min
        end_dict["TAVG"] = avg
        end_dict["TMAX"] = max
        end_list.append(end_dict)
    return jsonify(end_list)
if __name__ == "__main__":
    app.run(debug=True)

