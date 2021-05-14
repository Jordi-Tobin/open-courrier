from app.dashboard import bp
from flask import render_template, request, jsonify
from flask_login import login_required
from app.model import CourrierEntrant, CourrierSortant, Service, TypeCourrier, Correspondant, Responsable, Users
import datetime
from operator import itemgetter


@bp.route('/index')
@bp.route('/')
@login_required
def index():
    incoming = CourrierEntrant.objects.count()
    outgoing = CourrierSortant.objects.count()
    services = Service.objects.count()
    types = TypeCourrier.objects.count()
    users = Users.objects.count()
    correspondants = Correspondant.objects.count()
    responsables = Responsable.objects.count()

    years = CourrierEntrant.objects.aggregate([{"$project": {"year": {"$year": "$enregistrement"}}},
                                               {"$group": {"_id": "$year"}},
                                               {'$sort': {'_id': -1}}])
    return render_template('dashboard/index.html', incoming=incoming, services=services, types=types,
                           outgoing=outgoing, correspondants=correspondants, users=users, responsables=responsables,
                           years=years)


@bp.route('/_stats')
def stats():
    get_year = request.args.get('year')
    try:
        actual_year = int(get_year)
    except TypeError:
        actual_year = datetime.datetime.now().year

    start_date = datetime.datetime.strptime(str(actual_year) + '-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_date = datetime.datetime.strptime(str(actual_year) + '-12-31 00:00:00', '%Y-%m-%d %H:%M:%S')

    ingoing = CourrierEntrant.objects.aggregate([{"$match": {
                                                    "enregistrement": {'$gte': start_date, '$lte': end_date}
                                                  }},
                                                 {"$project": {
                                                     "month": {"$month": "$enregistrement"},
                                                     "reference": 1
                                                  }},
                                                 {"$group": {
                                                     "_id": "$month",
                                                     "count": {"$sum": 1}
                                                  }},
                                                 {'$sort': {'_id': -1}}])

    outgoing = CourrierSortant.objects.aggregate([{"$match": {
                                                    "enregistrement": {'$gte': start_date, '$lte': end_date}
                                                 }},
                                                {"$project": {
                                                    "month": {"$month": "$enregistrement"},
                                                    "reference": 1
                                                 }},
                                                {"$group": {
                                                    "_id": "$month",
                                                    "count": {"$sum": 1}
                                                 }},
                                                {'$sort': {'_id': -1}}])

    ingoing_to_list = list(ingoing)
    months = [list(i.values())[0] for i in ingoing_to_list]
    # Les mois non trouves sont initialises a 0
    in_result = ingoing_to_list + [{'_id': i, 'count': 0} for i in list(range(1, 13)) if i not in months]
    in_result.sort(key=itemgetter('_id'))

    outgoing_to_list = list(outgoing)
    months = [list(i.values())[0] for i in outgoing_to_list]
    # Les mois non trouves sont initialises a 0
    out_result = outgoing_to_list + [{'_id': i, 'count': 0} for i in list(range(1, 13)) if i not in months]
    out_result.sort(key=itemgetter('_id'))

    return jsonify(ingoing=in_result, outgoing=out_result)
