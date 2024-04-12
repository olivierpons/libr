import copy

from django.contrib.admin import AdminSite
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from app.models.person_typed import PersonTyped

base_fields_to_exclude = ('date_creation', 'date_last_update',
                          'date_v_start', 'date_v_end')


class MyAdminSite(AdminSite):
    site_header = _("Administration")

    models_on_top = [  # 'Person', 'Address',
        'ChatDocument', 'DocumentFile', 'ImageFile']

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        if len(app_list):
            # ! custom sort:
            el = copy.deepcopy(app_list[0])
            el['models'] = [a for a in el['models']
                            if a['object_name'] in self.models_on_top]
            app_list[0]['models'] = [
                a for a in app_list[0]['models']
                if a['object_name'] not in self.models_on_top]
            el['name'] = _("Frequently needed")
            app_list.insert(0, el)

        return app_list


admin.site = MyAdminSite(name='my_admin')
admin.site.register(PersonTyped)
