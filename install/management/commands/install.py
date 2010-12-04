from django.core.management.base import BaseCommand, CommandError
from pip.util import get_installed_distributions
from pip.req import InstallRequirement, RequirementSet
import os, difflib

import logging

def _add_to_requirements_txt(name):
    def _check(name):
        try:
            return name in open("requirements.txt").read()
        except:
            pass
    if _check(name):
        logging.info("Found {0} in requirements.txt".format(name))
    else:
        logging.info("Adding {0} to requirements.txt".format(name))
        open("requirements.txt", "a").write("{0}\n".format(name))

def _add_to_installed_apps(name):
    def _check(name):
        from django.conf import settings
        return name in settings.INSTALLED_APPS
    if _check(name):
        logging.info("Found {0} in INSTALLED_APPS".format(name))        
    else:
        logging.info("Adding {0} to INSTALLED_APPS".format(name))        
        import ast
        source = open("settings.py").read()
        module = ast.parse(source, "settings.py")
        def _find_installed_apps_statement(module):
            for st in module.body:
                if "INSTALLED_APPS" in [t.id for t in st.targets]:
                    return st
            raise Exception("No INSTALLED_APPS TODO")
            
        st = _find_installed_apps_statement(module)
        last_element = st.value.elts[-1]
        lines = source.split("\n")
        last_line = lines[last_element.lineno-1].strip()
        print last_line[0]
        if last_line[0] in "'\"": quotechar = last_line[0]
        else: quotechar = "'"
        new_line = "{space}{quotechar}{name}{quotechar},".format(
            quotechar=quotechar,
            space=" "*last_element.col_offset,
            name=name)
        new_lines = lines[:last_element.lineno] + [new_line] + lines[last_element.lineno:]
        open("settings.py", "w").write("\n".join(new_lines))
        print("\n".join(difflib.unified_diff(lines, new_lines)))

class Command(BaseCommand):
    ## args = '<poll_id poll_id ...>'
    ## help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for name in args:
            req = InstallRequirement.from_line(name)
            if not req.check_if_exists():
                raise Exception("TODO")
            distribution = req.satisfied_by
            _add_to_requirements_txt(distribution.project_name)
            _add_to_installed_apps(
                difflib.get_close_matches(distribution.project_name,
                                          os.listdir(distribution.location))[0])
            
