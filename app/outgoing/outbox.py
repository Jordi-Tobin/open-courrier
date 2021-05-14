from app.outgoing import bp
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app.outgoing.forms import OutgoingForm
from app.model import CourrierSortant, TypeCourrier, Service, Correspondant, Users
from bson import ObjectId
import re
import json
import datetime


@bp.route('/outbox', methods=['GET', 'POST'])
@login_required
def outbox():
    form = OutgoingForm()
    default = [("Tous", "Tous")]
    form.type.choices = default + [(i["type_courrier"], i['type_courrier']) for i in TypeCourrier.objects.all()]
    form.emetteur.choices = default + [(i["initiales"], i['nom']) for i in Service.objects.all()]
    form.copie.choices = default + [(i["initiales"], i['nom']) for i in Service.objects.all()]
    form.destinataire.choices = default
    return render_template('outgoing/outbox.html', form=form)


@bp.route('/outbox/<path:reference>/', methods=['GET', 'POST'])
@login_required
def outbox_letter(reference):
    letter = CourrierSortant.objects.get(reference=reference).to_dict()
    print(letter)

    form = OutgoingForm()
    default_type = [(letter['type_courrier'], letter['type_courrier'])]
    form.type.choices = default_type + [(i["type_courrier"], i['type_courrier']) for i in TypeCourrier.objects.all()]

    default_emetteur = [(letter['emetteur'], letter['emetteur'])]
    form.emetteur.choices = default_emetteur + [(i["initiales"], i['nom']) for i in Service.objects.all()]

    default_copie = [(letter['emetteur'], letter['emetteur'])]
    form.copie.choices = default_copie + [(i["initiales"], i['nom']) for i in Service.objects.all()]

    form.destinataire.choices = [(letter['destinataire'], letter['destinataire'])]

    return render_template('outgoing/outbox_letter.html', letter=letter, form=form)


@bp.route('/_add_comment_outbox', methods=['GET', 'POST'])
@login_required
def add_comment_outbox():
    reference = request.args.get('reference')
    comment = request.args.get('comment')
    comment_dict = {'auteur': Users.objects.get(username=current_user.username),
                    'texte': comment,
                    'date_commentaire': datetime.datetime.now()}
    CourrierSortant.objects(reference=reference).update_one(push__commentaires=comment_dict)

    return jsonify({'auteur': current_user.username,
                    'texte': comment,
                    'date_commentaire': datetime.datetime.now().strftime('%d/%m/%Y')})


@bp.route('/_ajax_datatable_outgoing', methods=['GET', 'POST'])
@login_required
def ajax_datatables_outgoing():
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
    date_depart = args['date_depart']
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
        check_emetteur = Service.objects.get(initiales=emetteur)
        match_dict['$match']['emetteur'] = check_emetteur.id

    if destinataire == 'Tous':
        match_dict['$match']['destinataire'] = {"$exists": True}
    else:
        check_destinataire = Correspondant.objects.get(nom=destinataire)
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
    check_courriers = CourrierSortant.objects.aggregate(pipeline)

    liste_courriers = []

    for numero, i in enumerate(check_courriers, 1):
        total_items = numero

        dico = dict()
        dico['numero'] = numero
        check_type = TypeCourrier.objects.get(id=ObjectId(i['type_courrier']))
        dico['type'] = check_type.type_courrier
        dico['reference'] = i['reference']
        dico['objet'] = i['objet']
        dico['date_creation'] = i['date_creation'].strftime("%Y-%m-%d")
        dico['date_depart'] = i['date_depart'].strftime("%Y-%m-%d")

        check_emetteur = Service.objects.get(id=ObjectId(i['emetteur']))
        dico['emetteur'] = check_emetteur.nom

        check_destinataire = Correspondant.objects.get(id=ObjectId(i['destinataire']))
        dico['destinataire'] = check_destinataire.nom

        liste_copie = []
        for j in i['copie']:
            check_copie = Service.objects.get(id=ObjectId(j))
            liste_copie.append(check_copie.nom)
        dico['copie'] = liste_copie

        dico['fichier'] = i['fichier']
        dico['pieces_jointes'] = i['pieces_jointes']
        dico['traitement'] = i['traitement']

        liste_courriers.append(dico)

    result = dict()
    result['recordsTotal'] = total_items
    result['recordsFiltered'] = total_items
    result['data'] = liste_courriers

    print("DRAW: ", result)
    return jsonify(result)
