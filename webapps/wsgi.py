"""
WSGI config for webapps project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapps.settings')
# Import and execute the import_data_from_json_file function
from webapps.import_json import import_data_from_json_file, create_initial_table

import_data_from_json_file('Yummy/static/init/init_dishes.json')
create_initial_table()

application = get_wsgi_application()
