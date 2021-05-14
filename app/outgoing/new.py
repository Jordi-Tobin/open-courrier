from app.outgoing import bp
from flask import render_template, request
from flask_login import login_required
from app.outgoing.forms import OutgoingForm
from app.model import CourrierSortant, CourrierEntrant, TypeCourrier, Service, Correspondant
from app.helpers import handle_uploaded_files


@bp.route('/new_outgoing', methods=['GET', 'POST'])
@login_required
def new_outgoing():
    form = OutgoingForm()
    form.type.choices = [(i["type_courrier"], i['type_courrier']) for i in TypeCourrier.objects.all()]
    form.emetteur.choices = [(i["initiales"], i['nom']) for i in Service.objects.all()]
    form.copie.choices = [(i["initiales"], i['nom']) for i in Service.objects.all()]

    if request.method == 'POST':
        uploaded_file = request.files.to_dict()   # getlist('file')
        files = []
        for i in uploaded_file:
            print(uploaded_file[i].filename)
            files.append(uploaded_file[i])

        fichier, *pieces_jointes = files
        filename, thumbnail = handle_uploaded_files(fichier, "Sortant")

        pj_names = pj_thumbnails = []
        for i in pieces_jointes:
            pj_name, pj_thumbnail = handle_uploaded_files(i, "Sortant")
            pj_names.append(pj_name)
            pj_thumbnails.append(pj_thumbnail)

        check_type_courrier = TypeCourrier.objects.get(type_courrier=request.form.get('type'))
        check_emetteur = Service.objects.get(initiales=request.form.get('emetteur'))
        check_destinataire = Correspondant.objects.get(nom=request.form.get('destinataire'))

        print(request.form.get('copie'), type(request.form.get('copie')))

        # Recuperation des services en copie
        copies = []
        if request.form.get('copie') != 'null' and request.form.get('copie') is not None:
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
        if request.form.get('liens') != 'null' and request.form.get('liens') is not None:
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

        courrier = CourrierSortant(type_courrier=check_type_courrier,
                                   reference=request.form.get('reference'),
                                   objet=request.form.get('objet'),
                                   date_courrier=request.form.get('date_depart'),
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
    return render_template('outgoing/new_outgoing.html', form=form)
