from flask import Blueprint

bp = Blueprint('panel', __name__)

from app.panel import routes