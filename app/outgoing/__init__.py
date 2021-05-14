# -*- coding:utf-8 -*-
from flask import Blueprint

bp = Blueprint('outgoing', __name__)

from app.outgoing import outbox, new
