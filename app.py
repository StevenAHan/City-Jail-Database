from re import I
from flask import Flask, render_template, request, url_for, flash, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

app = Flask(__name__)


# Default route
@app.route("/")
def index():
    return render_template("index.html")

    
if __name__ == "__main__":
    app.run(debug=True)