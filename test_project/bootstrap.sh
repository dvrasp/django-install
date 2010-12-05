#!/bin/sh
virtualenv env
. env/bin/activate
easy_install pip
python manage.py syncdb
cd .. ; python setup.py clean sdist && pip install dist/django-install-0.1.tar.gz  ; cd -
