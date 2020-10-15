import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
import datetime as dt
import yfinance as yf
from pandas_datareader import data as pdr
from model import screener

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route("/BSE")
def BSE():
    return render_template("BSE.html")

@app.route("/NSE")
def NSE():
    return render_template("NSE.html")


@app.route("/NSE_filtered", methods=["GET", "POST"])
def NSE_filtered():
    
    ret_message = [] 
    obj = screener()
    a, b, c = obj.screen()

    for i, j, k in zip(a, b, c):
        d = {}
        d["stock"] = i 
        d["rank"] = j
        d["eod_price"] = k 
        
        ret_message.append(d)
    

    return render_template("NSE_filtered.html", solution_text=ret_message)

@app.route("/BSE_filtered", methods=["GET", "POST"])
def BSE_filtered():
    
    ret_message = ["Not implemented yet!"]
    return render_template("BSE_filtered.html", solution_text=ret_message)




if __name__ == "__main__":
    app.run(debug=True)
