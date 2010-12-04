from django.core.management.base import BaseCommand, CommandError
from django.db import models

from optparse import make_option

class Command(BaseCommand):
    args = '<app_name app_name ...>'
    help = 'Examine models of the given app and outputs a Django admin.py module.'

    option_list = BaseCommand.option_list + (
        make_option('--modeladmin',
            action='store_true',
            dest='with_model_admin',
            default=False,
            help='with ModelAdmin stubs'),
        )
    REGISTRATION_FORMAT = """admin.site.register({name})"""
    REGISTRATION_FORMAT_WITH_MODELADMIN = """class {name}Admin(admin.ModelAdmin):
    pass
admin.site.register({name}, {name}Admin)
"""
    FORMAT = """from django.contrib import admin
from {app_name}.models import {model_names}

{registrations}
"""

    def handle(self, *args, **options):
        app_name = args[0]
        def get_models(app_name):
            for model in models.get_models():
                if model.__module__.split(".")[0] == app_name:
                    yield model
        app_models = get_models(app_name)
        model_names = [m.__name__ for m in app_models]
        if options.get('with_model_admin', False):
            registration_format = self.REGISTRATION_FORMAT_WITH_MODELADMIN
        else:
            registration_format = self.REGISTRATION_FORMAT
        registrations = "\n".join(
            [registration_format.format(name=name)
             for name in model_names])
        print (self.FORMAT.format(app_name=app_name,
       model_names=", ".join(model_names),
       registrations=registrations))
            
