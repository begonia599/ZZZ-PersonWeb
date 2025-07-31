from flask import Blueprint

drive_bp = Blueprint('drive', __name__)

from . import routes