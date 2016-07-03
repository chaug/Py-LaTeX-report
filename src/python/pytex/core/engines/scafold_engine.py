import datetime
import json
import os
import pystache
import shutil

from pytex import PYTEX_TEMPLATES_PATH, PYTEX_PROJECTS_PATH
from pytex.core.management.base import CommandError
from pytex.utils.importlib      import import_module

class Engine(object):

    TEMPLATES = []

    @classmethod
    def templates(cls):
        if cls.TEMPLATES:
            return cls.TEMPLATES
        try:
            cls.TEMPLATES = [
                f
                for f in os.listdir(PYTEX_TEMPLATES_PATH)
                if not f.startswith('_') and os.path.isdir(os.path.join(PYTEX_TEMPLATES_PATH,f))
            ]
        except OSError:
            pass
        return cls.TEMPLATES

    @staticmethod
    def safe_mkdir(path):
        if os.path.exists(path):
            if not os.path.isdir(path):
                raise CommandError("%s exists but is not a folder" % path)
        else:
            os.mkdir(path)

    def __init__(self, command, **options):
        self.command = command
        self.__dict__.update(options)

    def load_project_class(self, name):
        module = import_module('pytex.projects.%s' % name)
        return module.Project(self)

    def log(self, *args, **pwargs):
        self.command.log(*args, **pwargs)

    def validate(self, templates):
        if not (templates or self.template_list):
            raise CommandError('Enter at least one TEMPLATE.')
        if not self.output:
            raise CommandError('Mandatory --ouput')
        self.destination = os.path.abspath(self.output)
        parent = os.path.dirname(self.destination)
        if not os.path.isdir(parent):
            raise CommandError("%s doesn't exist or is not a folder" % parent)
        self.safe_mkdir(self.destination)
        return True

    def validate_template(self, template):
        return template in self.templates()

    def pre_run(self):
        self.log(1,"=========== PRE_RUN")
        if self.template_list:
            self.log(0, "LIST OF: %s" % PYTEX_TEMPLATES_PATH)
            self.log(0, "\n".join([" - %s" % tpl for tpl in self.templates()]))
        self.log(1,"===========")

    def render_file(self, fromPath, toPath, filename, rule = None, env = None, project = None):
        used_rule = {
            "action"    : "copy",
            "overwrite" : False,
            "new_name"  : None, # Means same as template
            "loop_on"   : None,
        }
        used_rule.update(rule or {})
        bn, ext  = os.path.splitext(filename)
        used_env = {
            "filename"  : filename,
            "basename"  : bn,
            "extension" : ext,
        }
        used_env.update(env or {})

        loop_on = used_rule["loop_on"] or []
        dimensions = []
        for dim in loop_on:
            if dim not in used_env:
                raise Exception("dimension {0} should be defined in configuration".format(dim))
            values = used_env.pop(dim)
            dimensions.append((dim, values))
        def _loop(dims):
            if dims:
                remaining_dims  = dims[1:]
                dimkey, values = dims[0]
                for value in (values if isinstance(values,list) else [values] ):
                    key = {} if value is None else { dimkey : value }
                    if remaining_dims:
                        for child_key in _loop(remaining_dims):
                            key.update(child_key)
                            yield key
                    else:
                        yield key
            else:
                yield {}

        overwrite = not not used_rule.get("overwrite")
        fn_rule   =         used_rule.get("new_name")
        action    =         used_rule.get("action") or "copy"

        fullSrc   = os.path.join(fromPath,filename)
        fullpaths = set()
        for key in _loop(dimensions):
            used_env["loop"] = key
            generated = pystache.render(
                fn_rule,
                used_env
            ) if fn_rule else filename

            dest     = os.path.join(toPath,generated) if toPath else generated
            fullDest = os.path.join(self.destination,dest)

            self.log(2, "From %s / %s" % (filename,  repr(key)))
            self.log(2, "Have to generate %s" % generated)

            if dest in self.exclusions or fullDest in fullpaths:
                self.log(2, "excluded")
                continue

            fullpaths.add(fullDest)
            if os.path.exists(fullDest):
                if overwrite:
                    os.unlink(fullDest)
                else:
                    self.log(2, "generation skip")
                    continue
            self.log(2, "Render with %s: %s to %s" % (action, filename, generated))
            if action == "mustache":
                self.render_mustache(fullSrc,fullDest, env = used_env)
            elif action.startswith("project"):
                method = action.partition("project.")[2]
                if not (hasattr(project,method) and callable(getattr(project,method))):
                    raise Exception("Project has no callable method: %s" % method)
                getattr(project,method)(fullSrc,fullDest, env = used_env)
            else:
                shutil.copy(fullSrc,fullDest)
        return list(fullpaths)

    def render_folder(self, fromPath, toPath, **args):
        for child in os.listdir(fromPath):
            fullChild = os.path.join(fromPath,child)
            if os.path.isdir(fullChild):
                dest = os.path.join(toPath,child) if toPath else child
                self.safe_mkdir(os.path.join(self.destination,dest))
                self.render_folder(fullChild,dest,**args)
            elif os.path.isfile(fullChild):
                self.render_file(
                    fromPath, toPath,
                    child,
                    **args
                )
        return os.path.join(self.destination,toPath)

    def write_data(self, filename, data):
        fullDest = os.path.join(self.destination,"data",filename)
        with open(fullDest,"wb") as oio:
            json.dump(data, oio
                , indent=4
            )

    def render_mustache(self, fullSrc, fullDest, env = None):
        oio = open(fullDest,"wb")
        iio = open(fullSrc ,"rb")
        src = iio.read()
        try:
            oio.write(pystache.render(src, env or {}))
        finally:
            iio.close()
            oio.close()

    def run(self, template):
        self.log(1, "SCAFOLD: %s" % template)

        for path in "sql data scafold user".split():
            fullpath = os.path.join(self.destination,path)
            self.safe_mkdir(fullpath)

        now = datetime.datetime.now()
        env0 = {
            "template"  : template,
            "today_Ymd" : "{0:%Y%m%d}".format(now),
            "today"     : "{0:%d-%b-%Y}".format(now),
            "timestamp" : "{0:%Y%m%d-%H%M%S}".format(now),
        }

        fromRoot = os.path.join(PYTEX_TEMPLATES_PATH,template)
        self.exclusions = set()

        config = self.render_file(fromRoot, "", "config.json")[0]
        if config and os.path.exists(config):
            with open(config) as io:
                env0.update(json.load(io))

        if env0.get("settings_todo"):
            raise Exception("Can't continue without setting [{0}]".format(",".join(env0["settings_todo"].keys())))

        sql_path = self.render_folder(os.path.join(fromRoot,"sql"), "sql", env = env0)

        project_name = template.replace("-","_")
        self.log(1, "PROJECT: %s" % project_name)
        project = self.load_project_class(project_name)
        if not project.setup_config(env0, sql_path):
            raise Exception("Invalid Project setup for {0}".format(project_name))

        environment = project.scafold_environment()
        self.write_data("project_environment.json", environment)
        env0.update(environment)
        self.write_data("full_environment.json", env0)

        scafold_rules = []
        scafold_rules_filename = os.path.join(fromRoot,"scafold_rules.json")
        if os.path.exists(scafold_rules_filename):
            with open(scafold_rules_filename) as io:
                scafold_rules = json.load(io)

        for rule in scafold_rules:
            source = rule["source"]
            folder,filename = os.path.split(source)
            self.render_file(
                os.path.join(fromRoot,folder),
                folder,filename,
                rule    = rule,
                env     = env0,
                project = project
            )
