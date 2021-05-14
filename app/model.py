from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
import datetime


class Users(db.Document):
    username = db.StringField(required=True, unique=True)
    email = db.StringField(required=True, unique=True)
    password_hash = db.StringField(max_length=120, required=True)
    role = db.IntField(default=2)
    profil = db.StringField(required=True)
    actif = db.BooleanField(default=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def __unicode__(self):
        return self.username

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self, *args, **kwargs):
        self.password_hash = generate_password_hash(self.password_hash)

        super(Users, self).save(*args, **kwargs)


@login.user_loader
def load_user(username):
    return Users.objects(username=username).first()


class Log(db.Document):
    titre = db.StringField()
    date = db.DateTimeField(default=datetime.datetime.now)
    user = db.ReferenceField(Users)

    def __repr__(self):
        return '<Log {}>'.format(self.titre)


class TypeCourrier(db.Document):
    type_courrier = db.StringField(required=True)
    actif = db.BooleanField(default=True)

    def __repr__(self):
        return '<TypeCourrier {}>'.format(self.type_courrier)

    def __unicode__(self):
        return self.type_courrier


class Responsable(db.Document):
    civilite = db.StringField(required=True)
    nom = db.StringField(required=True, unique=True)
    email = db.StringField(required=True, unique=True)
    telephone = db.StringField()
    actif = db.BooleanField(default=True)

    def __repr__(self):
        return '<Responsable {}>'.format(self.nom)

    def __unicode__(self):
        return self.nom


class Service(db.Document):
    nom = db.StringField(required=True)
    initiales = db.StringField()
    responsable = db.ReferenceField(Responsable)

    def __repr__(self):
        return '<Service {}>'.format(self.nom)

    def __unicode__(self):
        return self.nom


class Correspondant(db.Document):
    civilite = db.StringField(required=True)
    nom = db.StringField(required=True, unique=True)
    telephone = db.StringField()
    mail = db.StringField()
    entreprise = db.StringField()
    adresse = db.StringField(required=True)
    ville = db.StringField(required=True)
    actif = db.BooleanField(default=True)

    def __repr__(self):
        return '<Correspondant {}>'.format(self.nom)

    def __unicode__(self):
        return self.nom


class Commentaires(db.EmbeddedDocument):
    auteur = db.ReferenceField(Users)
    texte = db.StringField()
    date_commentaire = db.DateTimeField()

    def to_dict(self):
        commentaires = {
            'auteur': self.auteur.username,
            'texte': self.texte,
            'date_commentaire': self.date_commentaire,
        }
        return commentaires


class CourrierEntrant(db.Document):
    type_courrier = db.ReferenceField(TypeCourrier)
    reference = db.StringField(required=True)
    objet = db.StringField(required=True)
    date_arrivee = db.DateTimeField()
    date_creation = db.DateTimeField()
    emetteur = db.ReferenceField(Correspondant)
    destinataire = db.ReferenceField(Service)
    copie = db.ListField(db.ReferenceField(Service))
    fichier = db.StringField(required=True, unique=True)
    thumbnail = db.StringField(required=True)
    pieces_jointes = db.ListField()
    pj_thumbnails = db.ListField()
    liens = db.ListField()
    commentaires = db.ListField(db.EmbeddedDocumentField(Commentaires))
    enregistrement = db.DateTimeField(default=datetime.datetime.now)
    traitement = db.BooleanField(default=False)
    supprime = db.BooleanField(default=False)

    def __repr__(self):
        return '<CourrierEntrant {}>'.format(self.reference)

    def __unicode__(self):
        return self.reference

    def to_dict(self):
        courrier_entrant = {
            'type_courrier': self.type_courrier.type_courrier,
            'reference': self.reference,
            'objet': self.objet,
            'date_arrivee': self.date_arrivee,
            'date_creation': self.date_creation,
            'emetteur': self.emetteur.nom,
            'destinataire': self.destinataire.nom,
            'copie': [i.nom for i in self.copie],
            'fichier': self.fichier,
            'thumbnail': self.thumbnail,
            'pieces_jointes': self.pieces_jointes,
            'pj_thumbnails': self.pj_thumbnails,
            'liens': [i.to_dict() for i in self.liens],
            'commentaires': [i.to_dict() for i in self.commentaires],
            'enregistrement': self.enregistrement,
            'courrier': 'Entrant'
            # {k: (v.username if k == 'auteur' else v) for k, v in self.commentaires}
        }
        return courrier_entrant


class CourrierSortant(db.Document):
    type_courrier = db.ReferenceField(TypeCourrier)
    reference = db.StringField(required=True)
    objet = db.StringField(required=True)
    date_depart = db.DateTimeField()
    date_creation = db.DateTimeField()
    emetteur = db.ReferenceField(Service)
    destinataire = db.ReferenceField(Correspondant)
    copie = db.ListField(db.ReferenceField(Service))
    fichier = db.StringField(required=True, unique=True)
    thumbnail = db.StringField(required=True)
    pieces_jointes = db.ListField()
    pj_thumbnails = db.ListField()
    liens = db.ListField()
    commentaires = db.ListField(db.EmbeddedDocumentField(Commentaires))
    enregistrement = db.DateTimeField(default=datetime.datetime.now)
    traitement = db.BooleanField(default=False)
    supprime = db.BooleanField(default=False)

    def __repr__(self):
        return '<CourrierSortant {}>'.format(self.reference)

    def __unicode__(self):
        return self.reference

    def to_dict(self):
        courrier_sortant = {
            'type_courrier': self.type_courrier.type_courrier,
            'reference': self.reference,
            'objet': self.objet,
            'date_depart': self.date_depart,
            'date_creation': self.date_creation,
            'emetteur': self.emetteur.nom,
            'destinataire': self.destinataire.nom,
            'copie': ','.join([i.nom for i in self.copie]),
            'fichier': self.fichier,
            'thumbnail': self.thumbnail,
            'pieces_jointes': self.pieces_jointes,
            'pj_thumbnails': self.pj_thumbnails,
            'liens': [i.to_dict() for i in self.liens],
            'commentaires': [i.to_dict() for i in self.commentaires],
            'enregistrement': self.enregistrement,
            'courrier': 'Sortant'
        }
        return courrier_sortant
