import datetime
import json
import os
import pystache
import shutil

from pytex import PYTEX_TEMPLATES_PATH, PYTEX_PROJECTS_PATH
from pytex.core.management.base import CommandError

class Engine(object):

    TEMPLATES = []

    @classmethod
    def create(cls, **options):
        return cls(**options)

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

    def __init__(self, **options):
        self.__dict__.update(options)

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
        print "=========== PRE_RUN"
        if self.template_list:
            print "LIST OF:", PYTEX_TEMPLATES_PATH
            print "\n".join([" - %s" % tpl for tpl in self.templates()])
        print "==========="

    def render_file(self, fromPath, toPath, filename, env = None, overwrite = False):
        fullSrc  = os.path.join(fromPath,filename)

        line = os.popen("grep PYTEX_FILENAME " + fullSrc).read()
        generated = pystache.render(
            line.partition("PYTEX_FILENAME:")[2].strip(), env
        ) if line else filename

        dest     = os.path.join(toPath,generated) if toPath else generated
        fullDest = os.path.join(self.destination,dest)
        if dest in self.exclusions:
            return
        self.exclusions.add(dest)
        if os.path.exists(fullDest):
            if overwrite:
                os.unlink(fullDest)
            else:
                return fullDest
        if env is None:
            # copy
            shutil.copy(fullSrc,fullDest)
        else:
            # pystache render
            with open(fullSrc,"rb") as iio:
                with open(fullDest,"wb") as oio:
                    oio.write(
                        pystache.render(
                            iio.read(),
                            env
                        )
                    )
        return fullDest

    def traverse(self, fromPath, toPath, env):
        for child in os.listdir(fromPath):
            fullChild = os.path.join(fromPath,child)
            if os.path.isdir(fullChild):
                dest = os.path.join(toPath,child) if toPath else child
                self.safe_mkdir(os.path.join(self.destination,dest))
                self.traverse(fullChild,dest,env)
            elif os.path.isfile(fullChild):
                self.render_file(
                    fromPath, toPath,
                    child,
                    env       = env,
                    overwrite = not toPath.startswith("user")
                )

    def run(self, template):
        print "SCAFOLD:", template

        for path in "data scafold user".split():
            fullpath = os.path.join(self.destination,path)
            self.safe_mkdir(fullpath)

        now = datetime.datetime.now()
        env0 = {
            "template"  : template,
            "today_key" : "{0:%Y%m%d}".format(now),
            "today"     : "{0:%d-%b-%Y}".format(now),
            "timestamp" : "{0:%Y%m%d-%H%M%S}".format(now),
        }

        fromRoot = os.path.join(PYTEX_TEMPLATES_PATH,template)
        self.exclusions = set()

        config = self.render_file(fromRoot, "", "config.json")
        if config and os.path.exists(config):
            with open(config) as io:
                env0.update(json.load(io))

        print "ENV"
        print json.dumps(env0,indent=2)

        project = template.replace("-","_")
        print "PROJECT:", project
        # TODO : load and run project

        self.traverse(fromRoot,"",env0)
