#!/usr/bin/env python
from django.core.management import execute_manager, handle_default_options, setup_environ
import sys, os
sys.path.append(os.getcwd())

try:
    import settings
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the current directory %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % os.getcwd())
    sys.exit(1)
    
if __name__ == "__main__":
    from django_install.management.commands import install

    ## ## TODO
    ## import logging
    ## logging.basicConfig(level=logging.DEBUG)

    ## TODO
    cmd = install.Command()
    parser = cmd.create_parser(__file__, "install")
    options, args = parser.parse_args(sys.argv)
    setup_environ(settings)
    handle_default_options(options)
    cmd.handle(*args[1:]) ## TODO

