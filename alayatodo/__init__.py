from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


# configuration
DATABASE = 'alayatodo.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.getcwd() + '/' + DATABASE
SQLALCHEMY_TRACK_MODIFICATIONS = False
JSONIFY_PRETTYPRINT_REGULAR = True

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)
