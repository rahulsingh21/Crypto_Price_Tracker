
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import dotenv

import urllib
import os
import json
import datetime
from utils import DateCondition, get_from_and_to_from_date, send_alert

"""Initialisation of Flask App and SqlAlchemy DB"""
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crypto.db'
db = SQLAlchemy(app)
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

# ---------------DB Models and Functions-------------------------------

class Price(db.Model):
    """This is a Model class which maps with the `prices` table in database

    Args:
        id          : Integer   => Primary Key/Autofilled/AutoIncrement
        timestamp   : Timestamp => default(Current Time)
        coin        : Text      => Not nullable/default(BTC)
        price       : Numeric   => Not nullable

    Returns:
        Object of Price
    """
    __tablename__ = "prices"
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    coin = db.Column(db.TEXT, nullable=False, default="BTC")
    price = db.Column(db.Numeric, nullable=False)
    
    def __repr__(self):
        rep = {}
        rep['timestamp'] = self.timestamp.strftime('%d-%m-%Y %H:%M:%S')
        rep['price'] = int(self.price)
        rep['coin'] = self.coin
        return str(rep)
    

# -------------------------------ApScheduler Function-------------------------  

def get_btc_price():
    """
    Will get the latest market price of BTC from coingecko api
    The price will be inserted in the database along with the coin name and timestamp. 
    """
    
    # Extracting data from api and storing it in a dictionary
    url = "https://api.coingecko.com/api/v3/coins/bitcoin?localization=false&tickers=false"\
            "&market_data=true&community_data=false&developer_data=false&sparkline=false"
    response = urllib.request.urlopen(url)
    data = response.read()
    dict = json.loads(data)
    
    # Creating an instance of Price Model and inserting the data in DB
    price_of_btc = Price(coin="BTC", price = dict["market_data"]['current_price']["usd"])
    db.session.add(price_of_btc)
    db.session.commit()
    print(f"Added in DB coin : BTC, price : {dict['market_data']['current_price']['usd']}")
    
    # Triggering the alert email if out of range
    if not int(os.environ['MIN']) <= int(price_of_btc.price) <= int(os.environ['MAX']):
        upper_or_lower = 'upper' if int(price_of_btc.price) > int(os.environ['MAX']) else 'lower'
        threshold = os.environ['MIN'] if upper_or_lower == 'lower' else os.environ['MAX']
        send_alert(price_of_btc.price, upper_or_lower,  threshold)


# -------------------------------Flask Routes------------------------------

@app.route('/')
@app.route("/minmax")
def min_max():
    """This function is used to display form to the user
    to accept min, max and emailId

    Returns:
        Renders an html form template
    """
    return render_template("set_min_max.html")


@app.route('/setminmax',methods=['post'])
def set_min_max():
    """This function gets called when the form of '/minmax' is submitted.
    The form data are passed as post and are stored in .env file

    Returns:
        Redirects to '/showminmax' which displays the new min and max
    """
    min = request.form.get('min', type = str)
    max = request.form.get('max', type = str)
    email = request.form.get('email', type = str)
        
    os.environ["MIN"] = min if min else os.environ["MIN"]
    os.environ["MAX"] = max if max else os.environ["MAX"]
    os.environ["ALERT_EMAIL"] = email if email else os.environ["ALERT_EMAIL"]
    
    dotenv.set_key(dotenv_file, "MIN", os.environ["MIN"])
    dotenv.set_key(dotenv_file, "MAX", os.environ["MAX"])
    dotenv.set_key(dotenv_file, "ALERT_EMAIL", os.environ["ALERT_EMAIL"])
    
    return redirect(url_for("show_min_max"))


@app.route('/showminmax')
def show_min_max():
    """Shows the current min and max for the application

    Returns:
        Renders an html page with the latest min max values.
    """
    result = {'MIN': os.environ["MIN"], 'MAX': os.environ["MAX"]}
    return render_template("show_min_max.html", form_data = result)


@app.route("/api/prices/<coin>", methods = ['get'])
def get_price_details(coin):
    """This function is used to get the price details that was fetched
    on a particular day.

    The arguments accpted via [get] method are:
        offset -> default = 0
        limit -> default = 100

    Args:
        coin : the name of the coin passed 

    Returns:
        _type_: _description_
    """
    response = {
        "url" : "",
        "next" : "",
        "count" : 0,
        "data" : [],
    }
    date = request.args.get('date', type = str)
    offset = request.args.get('offset', default  = 0, type = int)
    limit = request.args.get("limit", default = 100, type = int)
    
    date_condition = get_from_and_to_from_date(date)
    
    # Apply filters for date and coin name
    qry = db.session.query(Price).filter(Price.timestamp >= date_condition.start).filter(Price.timestamp < date_condition.end)\
        .filter(Price.coin == 'BTC')

    # Get the count of the rows
    count = len(qry.all())
    response['count'] = count
    
    # Current URL with the default values of offset and limit if not passed
    current_url = f"<{request.root_url[:-1]}{request.path}?date={date}&offset={offset}&limit={limit}>"
    response['url'] = current_url
    
    # New Url will be N/A if the next page in pagination is not available
    new_url = "N/A"
    if offset + limit < count:
        new_offset = offset + limit
        new_url = f"<{request.root_url[:-1]}{request.path}?date={date}&offset={new_offset}&limit={limit}>"
    response["next"] = new_url
        
    # Applying limit and offset to the query
    qry_with_limit = qry.limit(limit)
    qry_with_limit_offset = qry.offset(offset)
    
    data = qry_with_limit_offset.all()
    data_with_dict = list(map(lambda price: repr(price), data))
    
    response['data'] = data_with_dict
        
    return response
    
    

if __name__ == "__main__":
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(get_btc_price,'interval',seconds=30)
    sched.start()
    app.run()
