# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField, SelectField, StringField, FileField
from wtforms.validators import DataRequired, Optional


class OutgoingForm(FlaskForm):
    type = SelectField("Type de courrier*", validators=[DataRequired()])
    reference = StringField('Numero de reference*', validators=[DataRequired()])
    objet = StringField('Objet du courrier*', validators=[DataRequired()])
    date_depart = DateField("Date de depart*", format="%Y-%m-%d", validators=[DataRequired()])
    date_creation = DateField("Date de creation*", format="%Y-%m-%d", validators=[DataRequired()])
    emetteur = SelectField('Emetteur du courrier*', validators=[DataRequired()])
    destinataire = SelectField("Destinataire", validators=[DataRequired()])
    copie = SelectField("Services en copie", validators=[Optional()])
    fichier = FileField("Fichier", validators=[DataRequired()])
    liens = SelectField("Liens avec d'autres courriers", validators=[Optional()])

    valider = SubmitField("Valider")
