"""APIs for delivering information from the database to the app."""
from flask import Blueprint, render_template
from flask_restful import Resource, Api, reqparse

MAIN_BLUEPRINT = Blueprint('main', __name__)

@MAIN_BLUEPRINT.route('/')
def index():
    return render_template("index.html")

API_BLUEPRINT = Blueprint("api", __name__, url_prefix="/api")
PERF_API = Api(API_BLUEPRINT)

class TableNames(Resource):
    """Returns a list of subtable names for perf_report."""
    def get(self):
        return "hi"

PERF_API.add_resource(TableNames, '/table_names/')