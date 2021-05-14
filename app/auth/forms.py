# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class Login(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    # remember_me = BooleanField('Se souvenir de moi')
