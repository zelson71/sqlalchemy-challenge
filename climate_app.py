import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, render_template, flash, logging, redirect, url_for, session, request, jsonify


######################################## Database Setup ########################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite",
                       connect_args={'check_same_thread': False}, echo=True)

######################################## Reflect Database ########################################

Base = automap_base()
######################################## Refelct the tables ########################################
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create the session
session = Session(engine)

######################################## Define Functions to use within our APP#####################################


def daily_normals(date):
    """Daily Normals.

    Args:
        date (str): A date string in the format '%m-%d'

    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax

    """

    sel = [func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()


######################################## Flask Setup ########################################
app = Flask(__name__)


######## Build the Flask Routes ######
######################################## List all routes that are available ########################################
######################################## With Rendered Web Page ########################################
@app.route("/")
def home():
    return render_template('index.html')


@app.route("/api/v1.0/precipitation")
def prcp():
    # Docstring
    """Return a list of precipitations from last year"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    max_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()

    # Get the first element of the tuple
    max_date = max_date[0]

    # Calculate the date 1 year ago from most recent date it the DataBase

    year_ago = dt.datetime.strptime(
        max_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prcip = session.query(
        Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    # Convert list of tuples into normal list
    prcip_dict = dict(prcip)

    return jsonify(prcip_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query stations
    station_results = session.query(
        Measurement.station).group_by(Measurement.station).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(station_results))

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""

    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    max_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()

    # Get the first element of the tuple
    max_date = max_date[0]

    # Calculate the date 1 year ago from most recent date in database

    year_ago = dt.datetime.strptime(
        max_date, "%Y-%m-%d") - dt.timedelta(days=365)
    # Query tobs
    results_tobs = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.date >= year_ago).all()

    # Convert list of tuples into normal list
    tobs_data = list(results_tobs)

    return jsonify(tobs_data)


@app.route("/api/v1.0/temp/<start>")
def calc_temps(start=None):
    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

    start_date = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    start_list = list(start_date)
    return jsonify(start_list)


@app.route("/api/v1.0/temp/<start>/<end>")
def calc_temps2(start="2016-04-10", end="2017-04-18"):
    # Docstring
    # Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""

    dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    dates_list = list(dates)
    return jsonify(dates_list)


@app.route("/precipitation.py.jinja2", methods=['GET', 'POST'])
def webprecip():

    return render_template('precipitation.py.jinja2')


@app.route("/start", methods=['GET', 'POST'])
def webstart():

    return render_template('start.py.jinja2')


@app.route("/startend", methods=['GET', 'POST'])
def webstartend():

    return render_template('startandend.py.jinja2')


if __name__ == '__main__':
    app.run(debug=True)
