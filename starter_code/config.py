import os
from flask import Flask, render_template, request, redirect, url_for, abort,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys
# run with python3 app.py
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
app = Flask(__name__)

# TODO IMPLEMENT DATABASE URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SQLALCHEMY_DATABASE_URI = 'postgres://nikarichardson:Aveyond000@127.0.0.1:5432/fyyurapp'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI 
