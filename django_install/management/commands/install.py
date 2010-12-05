from django.core.management.base import BaseCommand, CommandError
from pip.util import get_installed_distributions
from pip.req import InstallRequirement, RequirementSet

import os, difflib, datetime
import subprocess
import logging


def _print_diff(filename, lines, new_lines):
    try:
       fromfiledate = datetime.datetime.fromtimestamp(os.stat(filename).st_mtime)
    except OSError:
       fromfiledate = ''
    print("\n".join(difflib.unified_diff(lines, new_lines,
                                         fromfile=filename, tofile=filename,
                                         fromfiledate=fromfiledate,
                                         tofiledate=datetime.datetime.now(),
                                         lineterm=''))
          +"\n")

def _add_to_requirements_txt(names):
    def _check(name):
        try:
            return name in open("requirements.txt").read()
        except:
            pass

    new_names = []

    for name in names:
        if _check(name):
            logging.info("Found {0} in requirements.txt".format(name))
        else:
            logging.info("Adding {0} to requirements.txt".format(name))
            new_names.append(name)

    if new_names:
        if os.path.exists("requirements.txt"):
            requirements = open("requirements.txt").read().split("\n")
        else:
            requirements = ["\n"]

        if not requirements[-1].strip(): ## replace trailing newline
            requirements = requirements[:-1]

        new_requirements = requirements + new_names

        _print_diff("requirements.txt", requirements, new_requirements)
        #open("requirements.txt", "a").write("{0}\n".format(name))
    

def _add_to_installed_apps(names):
    def _check(name):
        from django.conf import settings
        return name in settings.INSTALLED_APPS

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
    if last_line[0] in "'\"": quotechar = last_line[0]
    else: quotechar = "'"

    new_names = []
    for name in names:
        if _check(name):
            logging.info("Found {0} in INSTALLED_APPS".format(name))        
        else:
            logging.info("Adding {0} to INSTALLED_APPS".format(name))        
            new_names.append(name)
    added_lines = ["{space}{quotechar}{name}{quotechar},".format(
        quotechar=quotechar,
        space=" "*last_element.col_offset,
        name=name) for name in new_names]
    if added_lines:
        new_lines = lines[:last_element.lineno] + added_lines + lines[last_element.lineno:]
        _print_diff("settings.py", lines, new_lines)
        
HOOKS = {
    'APPNAMES':{'sorl-thumbnail':['sorl.thumbnail']},
    }

class Command(BaseCommand):
    ## args = '<poll_id poll_id ...>'
    ## help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        new_app_names = []
        new_package_names = []
        for name in args:
            req = InstallRequirement.from_line(name)
            if not req.check_if_exists():
                result = subprocess.call(["pip", "install", name])
                if not result == 0:
                    raise Exception("Install error")
                req = InstallRequirement.from_line(name)
                if not req.check_if_exists():
                    raise Exception("Installed package not found")

            distribution = req.satisfied_by
            new_package_names.append(distribution.project_name)
            
            def _get_app_names(name):
                ## try real package names
                packages = os.listdir(distribution.location)
                candidates = difflib.get_close_matches(name, packages)
                if candidates:
                    return [candidates[0]]
                return HOOKS['APPNAMES'].get(name, name)
            
            new_app_names += _get_app_names(distribution.project_name)
            
        _add_to_requirements_txt(new_package_names)
        _add_to_installed_apps(new_app_names)
            
