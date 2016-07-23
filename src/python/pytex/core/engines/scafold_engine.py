import datetime
import json
import os
import pystache
import shutil

from pytex import PYTEX_TEMPLATES_PATH, PYTEX_PROJECTS_PATH, PYTEX_TEXMF_PATH
from pytex.core.management.base import CommandError
from pytex.utils.importlib      import import_module
from pytex.utils.shell          import safe_mkdir,safe_mkdir_p

class Engine(object):

    CACHE_FOLDER     = "cache"
    DOCUMENT_FOLDER  = "document"
    SETTINGS_FOLDER  = "settings"
    TEMPLATES_FOLDER = "templates"

    WORKING_FOLDERS  = [
        CACHE_FOLDER,
        DOCUMENT_FOLDER,
        os.path.join(DOCUMENT_FOLDER, "latex", "images"),
        SETTINGS_FOLDER,
        TEMPLATES_FOLDER,
    ]

    AVAILABLE_TEMPLATES = []

    @classmethod
    def templates(cls):
        if cls.AVAILABLE_TEMPLATES:
            return cls.AVAILABLE_TEMPLATES
        try:
            cls.AVAILABLE_TEMPLATES = [
                f
                for f in os.listdir(PYTEX_TEMPLATES_PATH)
                if not f.startswith('_') and os.path.isdir(os.path.join(PYTEX_TEMPLATES_PATH,f))
            ]
        except OSError:
            pass
        return cls.AVAILABLE_TEMPLATES

    def __init__(self, command, **options):
        self.command      = command
        self.template     = None
        self.project_root = None
        self.__dict__.update(options)

    @property
    def     project_cache_path(self): return os.path.join(self.project_root, self.    CACHE_FOLDER)

    @property
    def  project_document_path(self): return os.path.join(self.project_root, self. DOCUMENT_FOLDER)

    @property
    def  project_settings_path(self): return os.path.join(self.project_root, self. SETTINGS_FOLDER)

    @property
    def project_templates_path(self): return os.path.join(self.project_root, self.TEMPLATES_FOLDER)

    @property
    def project_sql_templates_path(self): return os.path.join(self.project_templates_path, "sql")


    def load_json(self, filename):
        if filename and os.path.exists(filename):
            with open(filename) as io:
                return json.load(io)

    def log(self, *args, **pwargs):
        self.command.log(*args, **pwargs)

    def validate_template(self):
        return self.template and self.template in self.templates()

    def render_file(self, fromPath, toPath, filename, rule = None, env = None, project = None):
        used_rule = {
            "action"    : "copy",
            "overwrite" : False,
            "new_name"  : None, # Means same as template
            "loop_on"   : None,
            "exclude"   : None,
            "only"      : None,
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
        exclude = used_rule["exclude"] or []
        only    = used_rule["only"   ] or []
        dimensions = []
        for dim in loop_on:
            if dim not in used_env:
                raise Exception("dimension {0} should be defined in configuration".format(dim))
            values = used_env.pop(dim)
            if exclude:
                exvs = exclude.pop()
                if exvs is not None:
                    values = filter(lambda x: x["key"] not in exvs, values)
            if only:
                onlys = only.pop()
                if only is not None:
                    values = filter(lambda x: x["key"] in onlys, values)
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
            fullDest = os.path.join(self.project_root,dest)

            self.log(2, "From %s / %s" % (filename,  repr(key)))
            self.log(2, "Have to generate %s" % generated)

            if fullDest in fullpaths:
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
                safe_mkdir(os.path.join(self.project_root,dest))
                self.render_folder(fullChild,dest,**args)
            elif os.path.isfile(fullChild):
                self.render_file(
                    fromPath, toPath,
                    child,
                    **args
                )
        return os.path.join(self.project_root,toPath)

    def write_data(self, filename, data):
        fullDest = os.path.join(self.project_settings_path, filename)
        with open(fullDest,"wb") as oio:
            json.dump(data, oio
                , indent=4
            )

    def render_sql_query(self, filename, *args, **pwargs):
        fullpath = os.path.join(self.project_sql_templates_path,filename)
        if not os.path.exists(fullpath):
            raise Exception("SQL template doesn't exist {0}".format(fullpath))
        with open(fullpath,"rb") as iio:
            src = iio.read()
            renderer = pystache.Renderer(search_dirs=[self.project_sql_templates_path])
            return renderer.render(src, *args, **pwargs)

    def render_mustache(self, fullSrc, fullDest, env = None):
        oio = open(fullDest,"wb")
        iio = open(fullSrc ,"rb")
        src = iio.read()
        try:
            oio.write(pystache.render(src, env or {}))
        finally:
            iio.close()
            oio.close()

    def create_project_tree(self):
        for path in self.WORKING_FOLDERS:
            fullpath = os.path.join(self.project_root, path)
            safe_mkdir_p(fullpath)

    def copy_templates(self):
        self.log(1, "COPY TEMPLATES")
        self.log(1, "- from %s" % self.template)
        self.log(1, "-   to %s" % self.template)

        safe_mkdir(self.project_templates_path)
        for tmpl in [ "_common" , self.template ]:
            self.render_folder(
                os.path.join(PYTEX_TEMPLATES_PATH, tmpl),
                self.TEMPLATES_FOLDER,
                rule = {
                    "overwrite" : True
                }
            )
        self.create_project_tree()
        settings = self.render_file(self.project_templates_path, self.SETTINGS_FOLDER, "config.json")[0]
        env      = self.load_json(settings)
        if env.get("settings_todo"):
            self.log(0,"Don't forget to update : %s" % settings)
            for key in env["settings_todo"].keys():
                self.log(0," - {0}".format(key))

    def load_mustache_environment(self):
        now = datetime.datetime.now()

        mustache_env = {
            "TEXMF_PATH"    : PYTEX_TEXMF_PATH,
            "PROJECT_ROOT"  : self.project_root,
            "DOCUMENT_PATH" : self.project_document_path,
            "template"      : self.template,
            "today_Ymd"     : "{0:%Y%m%d}".format(now),
            "today"         : "{0:%d-%b-%Y}".format(now),
            "timestamp"     : "{0:%Y%m%d-%H%M%S}".format(now),
        }

        env = self.load_json(os.path.join(self.project_settings_path,"config.json"))
        mustache_env.update(env or {})

        if mustache_env.get("settings_todo"):
            raise Exception("Can't continue without setting [{0}]".format(",".join(mustache_env["settings_todo"].keys())))

        self.write_data("run_environment.json", mustache_env)
        return mustache_env

    def createProject(self):
        project_name = self.template.replace("-","_")
        self.log(1, "PROJECT: %s" % project_name)

        module   = import_module('pytex.projects.%s' % project_name)
        project  = module.Project(self)
        env      = self.load_mustache_environment()

        if not project.setup(env):
            raise Exception("Invalid Project setup for {0}".format(project_name))
        return project

    def scafold(self, project):
        env = project.full_env or project.load_environment()

        scafold_rules_filename = os.path.join(self.project_templates_path, "scafold_rules.json")
        scafold_rules = self.load_json(scafold_rules_filename) or []

        for rule in scafold_rules:
            source    = rule["source"]
            folder,filename = os.path.split(source)
            dest_path = rule.get("dest_path") or folder
            self.render_file(
                os.path.join(self.project_templates_path, folder),
                os.path.join(self.DOCUMENT_FOLDER       , dest_path),
                filename,
                rule    = rule,
                env     = env.copy(),
                project = project
            )
