from flask import Blueprint

ni = Blueprint('ni', __name__)

from . import views
