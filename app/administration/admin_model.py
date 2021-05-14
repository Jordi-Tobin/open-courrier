from flask_admin.contrib.mongoengine import ModelView


class UserView(ModelView):
    column_filters = ['username', 'email']
    column_searchable_list = ('username', 'email')

    form_choices = {
        'profil': [
            ('Admin', 'Admin'),
            ('Archiviste', 'Archiviste'),
            ('Consultant', 'Consultant')
        ],
        'role': [
            ('0', '0'),
            ('1', '1'),
            ('2', '2')
        ]
    }

    create_modal = True
    edit_modal = True
    can_export = True


class LogView(ModelView):
    column_filters = ['titre', 'user']
    column_searchable_list = ('titre', 'user')

    form_ajax_refs = {
        'user': {
            'fields': ['username']
        }
    }

    can_create = False
    can_delete = False
    can_edit = False


class TypeCourrierView(ModelView):
    column_filters = ['type_courrier']
    column_searchable_list = ['type_courrier']

    create_modal = True
    edit_modal = True


class ResponsableView(ModelView):
    column_filters = ['nom']
    column_searchable_list = ['nom']

    create_modal = True
    edit_modal = True


class ServiceView(ModelView):
    column_filters = ['nom']
    column_searchable_list = ['nom']

    create_modal = True
    edit_modal = True


class CorrespondantView(ModelView):
    column_filters = ['nom', 'civilite']
    column_searchable_list = ('nom', 'civilite')

    create_modal = True
    edit_modal = True


class CourrierEntrant(ModelView):
    can_create = False
    can_delete = False
    can_edit = False


class CourrierSortant(ModelView):
    can_create = False
    can_delete = False
    can_edit = False
