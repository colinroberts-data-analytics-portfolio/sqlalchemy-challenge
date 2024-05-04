#Import the dependencies.
import numpy as np

from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

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
    """List all available api routes."""
    return (
        f"Available Routes to Choose:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd(replace with actual date & erase this)<start><br/>"
        f"/api/v1.0/yyyy-mm-dd(replace with actual date & erase this)<start>/<end><br/>"
    )

# /api/v1.0/precipitation ------------------------------------------
@app.route("/api/v1.0/precipitation")
def precipitation():
    #session link from python to the db
    session = Session(engine)
    
    # find date 1 year ago from the last data point in db
    max_date = session.query(func.max(Measurement.date)).scalar()
    max_date = dt.datetime.strptime(max_date, '%Y-%m-%d')
    one_year_ago = max_date - dt.timedelta(days=365)

    # query prcp
    prcp_db = [Measurement.date, Measurement.prcp]
    results = session.query(*prcp_db).filter(Measurement.date >= one_year_ago).all()
    session.close() 

    # Convert list tuples to dict ---------------------------------
    precipitation_dict = {date: prcp for date, prcp in results if prcp is not None}

    return jsonify(precipitation_dict)


# /api/v1.0/stations ------------------------------------------
@app.route("/api/v1.0/stations")
def stations():
    # Create session link from python to the db
    session = Session(engine)
    
    # query stations
    results = session.query(Station.station, Station.name).all()
    session.close()  # Close the session after the query

    # Convert list of tuples into a normal list of dictionaries
    station_list = [{'station': station, 'name': name} for station, name in results]

    return jsonify(station_list)

# /api/v1.0/tobs ------------------------------------------
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # find most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
                          group_by(Measurement.station).\
                          order_by(func.count(Measurement.station).desc()).\
                          first()[0]

    # find the last date in the db for most active station
    last_date = session.query(func.max(Measurement.date))\
                .filter(Measurement.station == most_active_station).\
                scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')

    # find 1 year ago from the last date for most active station
    year_ago = last_date - dt.timedelta(days=365)

    # query date and temperatures for most active station over prev year
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == most_active_station).\
              filter(Measurement.date >= year_ago).\
              order_by(Measurement.date).all()
    
    session.close()  

    # convert list of tuples to dict
    tobs_list = [{'date': date, 'temperature': tobs} for date, tobs in results]

    return jsonify(tobs_list)

# /api/v1.0/start and end ------------------------------------------

# f"/api/v1.0/yyyy-mm-dd<start><br/>"
@app.route("/api/v1.0/yyyy-mm-dd<start>")
def start(start):
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
                                func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    session.close()
    stats1 = []

    for min,avg,max in result:
        tobs_list = {}
        tobs_list["Min"] = min
        tobs_list["Average"] = avg
        tobs_list["Max"] = max
        stats1.append(tobs_list)
        
    return jsonify(stats1)

# f"/api/v1.0/yyyy-mm-dd<start><br/>"
@app.route("/api/v1.0/yyyy-mm-dd<start>/<end>")
def start_end(start,end):
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
                func.max(Measurement.tobs)).filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()

    session.close()

    stats2 = []
    for min,avg,max in queryresult:
        tobs_list = {}
        tobs_list["Min"] = min
        tobs_list["Average"] = avg
        tobs_list["Max"] = max
        stats2.append(tobs_list)

    return jsonify(stats2)



# start the Flask server -------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)

