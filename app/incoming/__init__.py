# -*- coding:utf-8 -*-
from flask import Blueprint

bp = Blueprint('incoming', __name__)

from app.incoming import new, inbox, search_helper
