# -*- coding:utf-8 -*-
from flask import Flask
from flask_mongoengine import MongoEngine
from config import Config
from flask_login import LoginManager
from flask_jsglue import JSGlue
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.consts import ICON_TYPE_FONT_AWESOME
import flask_excel as excel
# from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import logging
from logging.handlers import RotatingFileHandler
import os
from redis import Redis
import rq
from flask_gravatar import Gravatar
from flask_babelex import Babel

app = Flask(__name__)
db = MongoEngine()
jsglue = JSGlue()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Veuillez vous connecter pour accéder à cette page'
gravatar = Gravatar(size=100, rating='g', default='identicon', force_default=False,
                    force_lower=False, use_ssl=False, base_url=None)

redis = Redis()
task_queue = rq.Queue('standard-tasks', connection=redis)
babel = Babel()

# photos = UploadSet('photos', IMAGES)


class HomeView(AdminIndexView):
    @expose('/')
    def index(self):
        courriers_entrant = CourrierEntrant.objects.count()
        courriers_sortant = CourrierSortant.objects.count()
        services = Service.objects.count()
        types = TypeCourrier.objects.count()
        users = Users.objects.count()
        correspondants = Correspondant.objects.count()
        responsables = Responsable.objects.count()

        return self.render('admin/index.html', courriers_entrant=courriers_entrant, courriers_sortant=courriers_sortant,
                           services=services, types=types, correspondants=correspondants, responsables=responsables,
                           users=users)


admin = Admin(name='courrier', base_template='admin_dash/layout.html', template_mode='bootstrap3',
              index_view=HomeView(menu_icon_type=ICON_TYPE_FONT_AWESOME, menu_icon_value='fa fa-home'))


def create_app(config_class=Config):
    app.config.from_object(config_class)

    db.init_app(app)
    redis.from_url(app.config['REDIS_URL'])
    jsglue.init_app(app)
    login.init_app(app)
    excel.init_excel(app)
    gravatar.init_app(app)
    babel.init_app(app)
    # configure_uploads(app, photos)
    # patch_request_class(app)

    admin.init_app(app)
    admin.add_view(UserView(Users, name='Utilisateurs', menu_icon_type=ICON_TYPE_FONT_AWESOME,
                            menu_icon_value='fa fa-user'))
    admin.add_view(ResponsableView(Responsable, name='Responsables de service', menu_icon_type=ICON_TYPE_FONT_AWESOME,
                                   menu_icon_value='fa fa-address-card'))
    admin.add_view(ServiceView(Service, name='Services', menu_icon_type=ICON_TYPE_FONT_AWESOME,
                               menu_icon_value='fa fa-tasks'))
    admin.add_view(CorrespondantView(Correspondant, name='Correspondants', menu_icon_type=ICON_TYPE_FONT_AWESOME,
                                     menu_icon_value='fa fa-users'))
    admin.add_view(TypeCourrierView(TypeCourrier, name='Types de courrier', menu_icon_type=ICON_TYPE_FONT_AWESOME,
                                    menu_icon_value='fa fa-tasks'))

    @babel.localeselector
    def get_locale():
        # Put your logic here. Application can store locale in
        # user profile, cookie, session, etc.
        return 'fr'

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.incoming import bp as incoming_bp
    app.register_blueprint(incoming_bp)

    from app.outgoing import bp as outgoing_bp
    app.register_blueprint(outgoing_bp)
    """
    from app.parametres import bp as parametres_bp
    app.register_blueprint(parametres_bp)
    """

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/courrier.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Courrier startup')

    return app


from app.model import Users, Responsable, Service, TypeCourrier, Correspondant, CourrierEntrant, CourrierSortant, Log
from app.administration.admin_model import UserView, LogView, ServiceView, CorrespondantView, TypeCourrierView, \
    ResponsableView
