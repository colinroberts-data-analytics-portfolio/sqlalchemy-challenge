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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Calculate the date one year ago from the last data point
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitations
    all_precipitations = {date: prcp for date, prcp in precipitation_data}
    return jsonify(all_precipitations)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Query all stations
    results = session.query(Station.station).all()
    session.close()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Query the dates and temperature observations of the most active station for the last year
    most_active_station = 'USC00519281'
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == most_active_station).\
              filter(Measurement.date >= '2016-08-23').all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    session = Session(engine)
    """Return TMIN, TAVG, TMAX."""
    try:
        # Validate start date
        start_date = dt.strptime(start, '%Y-%m-%d')
        if end:
            # Validate end date
            end_date = dt.strptime(end, '%Y-%m-%d')
            results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                      filter(Measurement.date >= start, Measurement.date <= end).all()
        else:
            results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                      filter(Measurement.date >= start).all()
    except ValueError:
        session.close()
        return jsonify({"error": "Date must be in YYYY-MM-DD format"}), 400
    except Exception as e:
        session.close()
        return jsonify({"error": str(e)}), 500

    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)





