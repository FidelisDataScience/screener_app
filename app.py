import numpy as np
import pandas as pd
from numpy.linalg import inv, det
from flask import Flask, request, jsonify, render_template

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
    
    ret_message = ["working!"]
    return render_template("NSE_filtered.html", solution_text=ret_message)

@app.route("/BSE_filtered", methods=["GET", "POST"])
def BSE_filtered():
    
    ret_message = ["Not implemented yet!"]
    return render_template("BSE_filtered.html", solution_text=ret_message)




if __name__ == "__main__":
    app.run(debug=True)
