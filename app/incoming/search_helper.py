from app.incoming import bp
from flask import request, jsonify
from flask_login import login_required
from app.model import CourrierSortant, CourrierEntrant, Correspondant
import re


@bp.route('/_search_correspondent', methods=['GET', 'POST'])
@login_required
def search_correspondent():
    """Cette fonction fait la recherche progressive d'un correspondant et rempli
    la liste d'auto-completion. Les infos trouvees servent a remplir le champ emetteur pour
    un courrier entrant et le champ destinataire pour un courrier sortant.
        :arg:
            q: query, recu progressivement via des requetes ajax
        :return:
            liste_correspondant: liste des correspondants sous JSON
    """
    q = request.args.get('q')
    print(q)
    regx = re.compile(str(q), re.IGNORECASE)
    request_db = Correspondant.objects(nom=regx)
    liste_correspondant = []
    for i in request_db:
        print(i)
        dico = dict()
        dico['nom'] = i.nom
        liste_correspondant.append(dico)

    return jsonify(liste_correspondant)


@bp.route('/_search_reference', methods=['GET', 'POST'])
@login_required
def search_reference():
    """Cette fonction permet de rechercher la reference d'un courrier deja enregistre pour la lier a un courrier
     en cours d'enregistrement. Elle combine les courriers entrants et sortants

            :arg:
                q: l'argument envoye via ajax progressivement pour la recherche et l'auto-completion cote client
            :return:
                liste_references: liste contenant les references qui correspondent a l'argument de la recherche
    """
    q = request.args.get('q')
    print(q)
    regx = re.compile(str(q), re.IGNORECASE)
    request_courriers_entrant = CourrierEntrant.objects(reference=regx)
    request_courriers_sortant = CourrierSortant.objects(reference=regx)
    liste_references = []

    for i in request_courriers_entrant:
        print(i)
        dico = dict()
        dico['reference'] = i.reference
        liste_references.append(dico)

    for i in request_courriers_sortant:
        print(i)
        dico = dict()
        dico['reference'] = i.reference
        liste_references.append(dico)

    return jsonify(liste_references)
