# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField, SelectField, StringField, FileField
from wtforms.validators import DataRequired, Optional, Length
from flask_wtf.file import FileAllowed
# from app import photos


class TagListField(StringField):
    """Stringfield for a list of separated tags"""

    def __init__(self, label='', validators=None, remove_duplicates=True, to_lowercase=False, separator=' ', **kwargs):
        """
        Construct a new field.
        :param label: The label of the field.
        :param validators: A sequence of validators to call when validate is called.
        :param remove_duplicates: Remove duplicates in a case insensitive manner.
        :param to_lowercase: Cast all values to lowercase.
        :param separator: The separator that splits the individual tags.
        """
        super(TagListField, self).__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates
        self.to_lowercase = to_lowercase
        self.separator = separator
        self.data = []

    def _value(self):
        print("HERE", self.data)
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(self.separator)]
            if self.remove_duplicates:
                self.data = list(self._remove_duplicates(self.data))
            if self.to_lowercase:
                self.data = [x.lower() for x in self.data]

    @classmethod
    def _remove_duplicates(cls, seq):
        """Remove duplicates in a case insensitive, but case preserving manner"""
        d = {}
        for item in seq:
            if item.lower() not in d:
                d[item.lower()] = True
                yield item


class IncomingForm(FlaskForm):
    type = SelectField("Type de courrier*", validators=[DataRequired()])
    reference = StringField('Numero de reference*', validators=[DataRequired()])
    objet = StringField('Objet du courrier*', validators=[DataRequired()])
    date_arrivee = DateField("Date d'arrivee*", format="%Y-%m-%d", validators=[DataRequired()])
    date_creation = DateField("Date de creation*", format="%Y-%m-%d", validators=[DataRequired()])
    emetteur = SelectField('Emetteur du courrier*', validators=[DataRequired()])
    destinataire = SelectField("Destinataire", validators=[DataRequired()])
    copie = SelectField("Services en copie", validators=[Optional()])
    copie_tags = TagListField("Services en copie", separator=",",
                              validators=[Length(max=8, message="You can only use up to 8 tags.")])
    fichier = FileField("Fichier", validators=[DataRequired()])
    liens = SelectField("Liens avec d'autres courriers", validators=[Optional()])

    valider = SubmitField("Valider")
