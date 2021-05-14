import datetime

from app.incoming import bp
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.incoming.forms import IncomingForm
from app.model import CourrierEntrant, TypeCourrier, Service, Correspondant, Users
from bson import ObjectId
import re
import json
import ast


@bp.route('/inbox', methods=['GET', 'POST'])
@login_required
def inbox():
    form = IncomingForm()
    default = [("Tous", "Tous")]
    form.type.choices = default + [(i["type_courrier"], i['type_courrier']) for i in TypeCourrier.objects.all()]
    form.destinataire.choices = default + [(i["initiales"], i['nom']) for i in Service.objects.all()]
    form.copie.choices = default + [(i["initiales"], i['nom']) for i in Service.objects.all()]
    form.emetteur.choices = default
    return render_template('incoming/inbox.html', form=form)


@bp.route('/inbox/<path:reference>/', methods=['GET', 'POST'])
@login_required
def inbox_letter(reference):
    letter = CourrierEntrant.objects.get(reference=reference).to_dict()

    form = IncomingForm()
    default_type = [(letter['type_courrier'], letter['type_courrier'])]
    form.type.choices = default_type + [(i["type_courrier"], i['type_courrier']) for i in TypeCourrier.objects.all()]

    default_destinataire = [(letter['destinataire'], letter['destinataire'])]
    form.destinataire.choices = default_destinataire + [(i["nom"], i['nom']) for i in Service.objects.all()
                                                        if i['nom'] != letter['destinataire']]

    print(type(letter['copie']), letter['copie'])
    form.copie_tags.default = letter['copie']

    form.emetteur.choices = [(letter['emetteur'], letter['emetteur'])]
    form.process()

    services = [i['nom'] for i in Service.objects.all()]  # for whitelist tagify

    return render_template('incoming/inbox_letter.html', letter=letter, services=services, form=form)


@bp.route('/_add_comment_incoming', methods=['GET', 'POST'])
@login_required
def add_comment():
    reference = request.args.get('reference')
    comment = request.args.get('comment')
    comment_dict = {'auteur': Users.objects.get(username=current_user.username),
                    'texte': comment,
                    'date_commentaire': datetime.datetime.now()}
    CourrierEntrant.objects(reference=reference).update_one(push__commentaires=comment_dict)

    return jsonify({'auteur': current_user.username,
                    'texte': comment,
                    'date_commentaire': datetime.datetime.now().strftime('%d/%m/%Y')})


@bp.route('/save_changes_incoming', methods=['GET', 'POST'])
@login_required
def save_changes_incoming():
    reference_id = request.args.get('reference_id')
    check_type_courrier = TypeCourrier.objects.get(type_courrier=request.form.get('type'))
    check_emetteur = Correspondant.objects.get(nom=request.form.get('emetteur'))
    check_destinataire = Service.objects.get(nom=request.form.get('destinataire'))
    check_copie = [Service.objects.get(nom=i.get('value')) for i in ast.literal_eval(request.form.get('copie_tags'))]

    CourrierEntrant.objects(reference=reference_id).update_one(set__type_courrier=check_type_courrier,
                                                               set__reference=request.form.get('reference'),
                                                               set__objet=request.form.get('objet'),
                                                               set__date_arrivee=request.form.get('date_arrivee'),
                                                               set__date_creation=request.form.get('date_creation'),
                                                               set__emetteur=check_emetteur,
                                                               set__destinataire=check_destinataire,
                                                               set__copie=check_copie)

    return redirect(url_for('incoming.inbox_letter', reference=request.form.get('reference')))


@bp.route('/_ajax_datatable_incoming', methods=['GET', 'POST'])
@login_required
def ajax_datatables_incoming():
    """Cette route rend les documents en fonction des cles de recherche definies. Elle construit un pipeline avec
    les cles transmises qui sera passe dans l'aggreation avec MongoDB
        :argument:
            num: numero de la page en cours (Datatables)
            site: nom du site
            departement: nom du departement
            service: nom du service
            search: mot-cle de recherche sur le libelle
        :return:
            result: liste des documents trouves apres aggregation + elements de pagination datatables
    """
    args = json.loads(request.values.get("args"))
    print(args)
    print(args['page_num'])
    print(args['search']['value'])
    num = int(args['page_num']) + 1
    type_courrier = args['type']
    emetteur = args['emetteur']
    destinataire = args['destinataire']
    statut = args['statut']
    date_arrivee = args['date_arrivee']
    search = args['search']['value']

    items_to_show = 100
    total_items = 0
    pipeline = []
    match_dict = dict()
    match_dict['$match'] = {}

    if len(search) > 1:
        regx = re.compile(str(search), re.IGNORECASE)
        match_dict['$match']['reference'] = regx
        match_dict['$match']['objet'] = regx
        match_dict['$match']['supprime'] = False
    else:
        match_dict['$match']['reference'] = {"$exists": True}
        match_dict['$match']['supprime'] = False

    if type_courrier == 'Tous':
        match_dict['$match']['type_courrier'] = {"$exists": True}
    else:
        check_type = TypeCourrier.objects.get(type_courrier=type_courrier)
        match_dict['$match']['type_courrier'] = check_type.id

    if emetteur == 'Tous':
        match_dict['$match']['emetteur'] = {"$exists": True}
    else:
        check_emetteur = Correspondant.objects.get(nom=emetteur)
        match_dict['$match']['emetteur'] = check_emetteur.id

    if destinataire == 'Tous':
        match_dict['$match']['destinataire'] = {"$exists": True}
    else:
        check_destinataire = Service.objects.get(initiales=destinataire)
        match_dict['$match']['destinataire'] = check_destinataire.id

    if statut == 'Tous':
        match_dict['$match']['traitement'] = {"$exists": True}
    elif statut == 'T':
        match_dict['$match']['traitement'] = True
    else:
        match_dict['$match']['traitement'] = False

    pipeline.append(match_dict)
    pipeline.append({"$skip": items_to_show * (num - 1)})
    pipeline.append({"$limit": items_to_show})
    print(pipeline)

    # check_document = Document.objects.all().skip(items_to_show * (num - 1)).limit(items_to_show)
    check_courriers = CourrierEntrant.objects.aggregate(pipeline)

    liste_courriers = []

    for numero, i in enumerate(check_courriers, 1):
        total_items = numero
        dico = dict()
        dico['numero'] = numero
        check_type = TypeCourrier.objects.get(id=ObjectId(i['type_courrier']))
        dico['type'] = check_type.type_courrier
        dico['reference'] = i['reference']
        dico['objet'] = i['objet']
        dico['date_creation'] = i['date_creation'].strftime("%d-%m-%Y")
        dico['date_arrivee'] = i['date_arrivee'].strftime("%d-%m-%Y")

        check_emetteur = Correspondant.objects.get(id=ObjectId(i['emetteur']))
        dico['emetteur'] = check_emetteur.nom

        check_destinataire = Service.objects.get(id=ObjectId(i['destinataire']))
        dico['destinataire'] = check_destinataire.nom

        liste_copie = []
        for j in i['copie']:
            check_copie = Service.objects.get(id=ObjectId(j))
            liste_copie.append(check_copie.nom)
        dico['copie'] = liste_copie

        dico['fichier'] = i['fichier']
        dico['pieces_jointes'] = i['pieces_jointes']
        dico['traitement'] = i['traitement']
        dico['enregistrement'] = i['enregistrement'].strftime("%d-%m-%Y")

        liste_courriers.append(dico)

    result = dict()
    result['recordsTotal'] = total_items
    result['recordsFiltered'] = total_items
    result['data'] = liste_courriers

    print("DRAW: ", result)
    return jsonify(result)
