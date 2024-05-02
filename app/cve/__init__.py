from flask import Blueprint

bp = Blueprint('cve', __name__)


from app.cve import routes