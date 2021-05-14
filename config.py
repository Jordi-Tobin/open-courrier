# -*- coding:utf-8 -*-
import os


class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'open-courrier-project@janvier-2021'
    MONGODB_DB = 'COURRIER'
    MONGODB_HOST = os.environ.get('DATABASE_URL') or "mongodb://localhost:27017/COURRIER"
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    SESSION_TYPE = 'filesystem'
    UPLOAD_PATH = 'app/static/uploads'
