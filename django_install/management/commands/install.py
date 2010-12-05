from django.core.management.base import BaseCommand, CommandError
from pip.util import get_installed_distributions
from pip.req import InstallRequirement, RequirementSet

from django_install.hooks import HOOKS

import os, difflib, datetime
import subprocess
import logging


def _print_diff(filename, lines, new_lines):
    try:
       fromfiledate = datetime.datetime.fromtimestamp(os.stat(filename).st_mtime)
    except OSError:
       fromfiledate = ''
    print("\n".join(difflib.unified_diff(lines, new_lines,
                                         fromfile="a/"+filename, tofile="b/"+filename,
                                         fromfiledate=fromfiledate,
                                         tofiledate=datetime.datetime.now(),
                                         lineterm=''))
          +"\n")

def _add_default_template(name, content): ## TODO TODO
    path = os.path.join("templates", name)
    if not os.path.exists(path):
        _print_diff(path, [], content.split("\n"))

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
    _settings_add_to_list("INSTALLED_APPS", names)
    
def _settings_add_to_list(variable_name, names):
    def _check(name):
        from django.conf import settings
        return name in getattr(settings, variable_name)

    import ast
    source = open("settings.py").read()
    module = ast.parse(source, "settings.py")

    class StatementNotFound(Exception): pass
    def _find_statement(module, variable_name):
        for st in module.body:
            try:
	  	if variable_name in [t.id for t in st.targets]:
                    return st
	    except AttributeError:
		continue
        raise StatementNotFound(variable_name)

    lines = source.split("\n")
    new_lines = lines
    quotechar = "'"
    
    def _format_value(v):
        if isinstance(v, str):
            return "{quotechar}{value}{quotechar}".format(value=v, quotechar=quotechar)
        else:
            return repr(v)
    
    try:
        ## try to add the value to an existing statement
        st = _find_statement(module, variable_name)
        last_element = st.value.elts[-1]
        last_line = lines[last_element.lineno-1].strip()
        if last_line[0] in "'\"": quotechar = last_line[0]
        else: quotechar = "'"

        new_names = []
        for name in names:
            if _check(name):
                logging.info("Found {0} in {1}".format(name, variable_name))        
            else:
                logging.info("Adding {0} to {1}".format(name, variable_name))        
                new_names.append(name)

        added_lines = ["{space}{value},".format(
            space=" "*last_element.col_offset,
            value=_format_value(v)) for v  in new_names]
        if added_lines:
            new_lines = lines[:last_element.lineno] + added_lines + lines[last_element.lineno:]
    except StatementNotFound:
        ## create a new one instead (before INSTALLED_APPS)
        st = _find_statement(module, "INSTALLED_APPS")
        ## values = "\n".join(["{space}{value},".format(value=_format_value(value))
        ##                     for value in names])
        added_lines = ["{space}{value},".format(
            space=" "*4,
            value=_format_value(v)) for v  in names]
        VARIABLE_LIST_FORMAT = """{name} = [
{values}
]
"""
        new_lines = lines[:st.lineno-1] \
                    + VARIABLE_LIST_FORMAT.format(name=variable_name, values="\n".join(added_lines)).split("\n") \
                    + lines[st.lineno-1:]

    if new_lines and not lines == new_lines:
        _print_diff("settings.py", lines, new_lines)

class Command(BaseCommand):
    args = '<package_name package_name ...>'
    help = 'Install packages using pip and outputs a patch with configuration settings'


    def handle(self, *args, **options):
        new_app_names = []
        new_package_names = []
        extra_settings = []
        default_templates = []
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
                if HOOKS['APPNAMES'].has_key(name):
                    return HOOKS['APPNAMES'][name]
                    
                ## try real package names
                packages = os.listdir(distribution.location)
                candidates = difflib.get_close_matches(name, packages)
                if candidates:
                    return [candidates[0]]
                
                return name
            
            new_app_names += _get_app_names(distribution.project_name)
            if HOOKS['EXTRA_SETTINGS'].has_key(distribution.project_name):
                extra_settings += [HOOKS['EXTRA_SETTINGS'][distribution.project_name]]
            if HOOKS['TEMPLATES'].has_key(distribution.project_name):
                default_templates += [HOOKS['TEMPLATES'][distribution.project_name]]
                
        _add_to_requirements_txt(new_package_names)

        ## settings
        for d in extra_settings:
            for name, values in d.items():
                _settings_add_to_list(name, values)
                
        for d in default_templates:
            for name, content in d.items():
                _add_default_template(name, content)

        _add_to_installed_apps(new_app_names)
