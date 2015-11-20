from flask import Blueprint

game = Blueprint('game', __name__)

from . import views, errors
from ..models import *


@game.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
