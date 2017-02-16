from flask import Blueprint

library = Blueprint('library', __name__)

from . import views, errors
from ..models import *


@library.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
