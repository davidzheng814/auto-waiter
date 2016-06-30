"""Initialize the app."""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)
APP.config.from_object('config')

@APP.errorhandler(404)
def not_found(error):
    """Return the 404 not found page."""
    return render_template('404.html'), 404

from app.views import *
APP.register_blueprint(MAIN_BLUEPRINT)
APP.register_blueprint(API_BLUEPRINT)
