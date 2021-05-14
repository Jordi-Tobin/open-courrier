from app.incoming import bp
from flask import render_template, request
from flask_login import login_required
from app.incoming.forms import IncomingForm
from app.model import CourrierEntrant, CourrierSortant, TypeCourrier, Service, Correspondant
from app.helpers import handle_uploaded_files


@bp.route('/new_incoming', methods=['GET', 'POST'])
@login_required
def new_incoming():
    form = IncomingForm()
    form.type.choices = [(i["type_courrier"], i['type_courrier']) for i in TypeCourrier.objects.all()]
    form.destinataire.choices = [(i["initiales"], i['nom']) for i in Service.objects.all()]
    form.copie.choices = [(i["initiales"], i['nom']) for i in Service.objects.all()]

    if request.method == 'POST':
        uploaded_file = request.files.to_dict()   # getlist('file')
        files = []
        for i in uploaded_file:
            print(uploaded_file[i].filename)
            files.append(uploaded_file[i])

        fichier, *pieces_jointes = files
        filename, thumbnail = handle_uploaded_files(fichier, "Entrant")

        pj_names = []
        pj_thumbnails = []
        for i in pieces_jointes:
            pj_name, pj_thumbnail = handle_uploaded_files(i, "Entrant")
            pj_names.append(pj_name)
            pj_thumbnails.append(pj_thumbnail)

        check_type_courrier = TypeCourrier.objects.get(type_courrier=request.form.get('type'))
        check_emetteur = Correspondant.objects.get(nom=request.form.get('emetteur'))
        check_destinataire = Service.objects.get(initiales=request.form.get('destinataire'))

        print(request.form.get('copie'), type(request.form.get('copie')))

        # Recuperation des services en copie
        copies = []
        if request.form.get('copie') != 'null':
            get_copie_list = request.form.get('copie').split(",")
            for i in get_copie_list:
                try:
                    check_copie = Service.objects.get(initiales=i)
                    copies.append(check_copie)
                except Service.DoesNotExist:
                    pass

        # Recuperation des courriers lies
        liens = []
        print(request.form.get('liens'), type(request.form.get('liens')))
        if request.form.get('liens') != 'null':
            get_liens = request.form.get('liens').split(",")
            for i in get_liens:
                try:
                    check_lien_entrant = CourrierEntrant.objects.get(reference=i)
                    liens.append(check_lien_entrant)
                except CourrierEntrant.DoesNotExist:
                    pass

                try:
                    check_lien_sortant = CourrierSortant.objects.get(reference=i)
                    liens.append(check_lien_sortant)
                except CourrierSortant.DoesNotExist:
                    pass

        courrier = CourrierEntrant(type_courrier=check_type_courrier,
                                   reference=request.form.get('reference'),
                                   objet=request.form.get('objet'),
                                   date_arrivee=request.form.get('date_arrivee'),
                                   date_creation=request.form.get('date_creation'),
                                   emetteur=check_emetteur,
                                   destinataire=check_destinataire,
                                   copie=copies,
                                   fichier=filename,
                                   thumbnail=thumbnail,
                                   pieces_jointes=pj_names,
                                   pj_thumbnails=pj_thumbnails,
                                   liens=liens)
        courrier.save()

        # return redirect(url_for('courriers.nouveau_courrier_entrant'))
    return render_template('incoming/new_incoming.html', form=form)
