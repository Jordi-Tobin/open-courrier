# -*- coding:utf-8 -*-
from flask import Blueprint

bp = Blueprint('dashboard', __name__)

from app.dashboard import home
