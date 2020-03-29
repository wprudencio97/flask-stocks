from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
db = SQLAlchemy(app)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(80), unique=False)
    date = db.Column(db.String(120), unique=False)
    open = db.Column(db.String(120), unique=False)
    high = db.Column(db.Float, unique=False)
    low = db.Column(db.Float, unique=False)
    close = db.Column(db.Float, unique=False)
    adj_close = db.Column(db.Float, unique=False)
    volume = db.Column(db.Float, unique=False)

db.create_all()

def main(ticker):
    stock_symbol = ticker

    #clear existing data
    db.session.query(Stock).delete()
    db.session.commit()

    # get the stock data
    stock_data = get_stock(stock_symbol)
    # populate the database
    populate_database(stock_symbol, stock_data, db)

def get_stock(stock_symbol):
    yf.pdr_override()

    start_year = 2020
    start_month = 1
    start_day = 1

    start = dt.datetime(start_year, start_month, start_day)
    now = dt.datetime.now()

    df = pdr.get_data_yahoo(stock_symbol, start, now)

    return df


def populate_database(stock_symbol, stock_data, db):
    df = stock_data

    for i in df.index:
        # insert the values into the database
        db.session.add(Stock(stock_name=stock_symbol, date=str(i), open=str(df['Open'][i]), high=float(df['High']
                                                                  [i]), low=float(df['Low'][i]), close=float(df['Close'][i]), adj_close=float(df['Adj Close'][i]), volume=float(df['Volume'][i])))
        db.session.commit()


@app.route('/')
def home():
    return render_template('home.html') 

@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
    if request.method == 'POST':
        ticker = request.form.get('ticker-symbol')
        main(ticker)
        return render_template('stocks.html',values=Stock.query.all())
    else:
        return render_template('stocks.html',values=Stock.query.all())

#run the program by running this app
if __name__ == "__main__":
    app.run(debug=True)