from flask import render_template
# from app.email import send_email
from app.errors import bp


@bp.app_errorhandler(403)
def access_forbidden(error):
    return render_template('errors/page_403.html'), 403


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/page_404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    """
    send_email("[U-PUBLIUS] log d'activité et bugs",
               sender=app.config['ADMINS'][0],
               recipients=app.config['ADMINS'],
               text_body='Fichier de log en attache'
               )
    """
    return render_template('errors/page_500.html'), 500
