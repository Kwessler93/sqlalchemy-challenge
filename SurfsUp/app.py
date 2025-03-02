# Import the dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, jsonify

import datetime as dt
import pandas as pd


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
Session = scoped_session(sessionmaker(bind=engine))

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session()

    # Calculate the date one year from the last date in data set.
    one_year_before = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    sel = [Measurement.date, Measurement.prcp]
    one_year_data = session.query(*sel).\
         filter(Measurement.date >= one_year_before).\
         all () 
    
    session.close()
    
    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    one_year_data = pd.DataFrame(one_year_data, columns=['date', 'prcp_inches'])

    # Sort the dataframe by date
    sorted_one_year_data = one_year_data.sort_values(by='date')

    precipitation_dict = sorted_one_year_data.set_index('date')['prcp_inches'].to_dict()

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session()

     # Query all stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session()

    one_year_before = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    sel = [Measurement.station, Measurement.date, Measurement.tobs]
    one_year_temp_data = session.query(*sel).\
        filter(Measurement.date >= one_year_before,
            Measurement.station == 'USC00519281').\
            all () 
    
    session.close()
    
    # Save the query results as a Pandas DataFrame. Explicitly set the column names 
    one_year_temp_data = pd.DataFrame(one_year_temp_data, columns=['station','date', 'temp'])

    temp_data_list = one_year_temp_data.to_dict(orient='records')

    return jsonify(temp_data_list)

@app.route("/api/v1.0/<start>")
def date_start(start):
    session = Session()

    results = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    session.close()

    if results[0][0] is None:
        return jsonify({"error": "No data found for the specified start date."}), 404

    temp_stats = {
        "TMIN": results[0][0],
        "TMAX": results[0][1],
        "TAVG": results[0][2]
    }

    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start, end):
    session = Session()

    results = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start, Measurement.date <= end).all()

    session.close()

    if results[0][0] is None:
        return jsonify({"error": "No data found for the specified date range."}), 404

    temp_stats = {
        "TMIN": results[0][0],
        "TMAX": results[0][1],
        "TAVG": results[0][2]
    }

    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)