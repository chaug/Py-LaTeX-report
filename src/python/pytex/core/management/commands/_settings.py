import json
import os

from pytex                      import PYTEX_PROJECT_SETTINGS, get_version
from pytex.core.management.base import CommandError

from pytex.utils.shell          import safe_mkdir

class ProjectSettings(object):

    @staticmethod
    def projectSettingsFile(path):
        return os.path.join(path, PYTEX_PROJECT_SETTINGS)

    @classmethod
    def findProjectRoot(cls, fromPath):
        path = os.path.abspath(fromPath)
        if not os.path.exists(path): return
        while path != "/" and not os.path.exists(cls.projectSettingsFile(path)):
            path, head = os.path.split(path)
        if os.path.exists(cls.projectSettingsFile(path)):
            return path

    def __init__(self, fromPath, persistent_options = None):
        self.persistent_options = persistent_options or []
        self.fromPath           = os.path.abspath(fromPath)
        self.root               = self.findProjectRoot(fromPath)
        self.file               = None

    def createAndComplete(self, **options):
        if not os.path.exists(self.fromPath):
            safe_mkdir(self.fromPath)

        root      = self.root or self.fromPath
        self.file = self.projectSettingsFile(root)

        optionChanged = [
            1
            for key in self.persistent_options
            if options.get(key)
        ]

        if optionChanged or not os.path.exists(self.file):
            with open(self.file,"w") as pio:
                json.dump(
                    {
                        "pytex" : {
                            "version" : get_version(),
                            "options" : dict((key, options.get(key)) for key in self.persistent_options)
                        }
                    },
                    pio
                    , indent = 4
                )
            self.root = root

        return self.complete(**options)

    def complete(self, **options):
        if not self.root:
            raise CommandError("No valid Project Root from %s" % self.fromPath)
        if not self.file:
            self.file = self.projectSettingsFile(self.root)

        settings = {}
        with open(self.file,"r") as pio:
            settings = json.load(pio)

        file_options = (settings.get("pytex") or {}).get("options") or {}

        completed_options = options.copy()

        for key in self.persistent_options:
            if not completed_options.get(key):
                completed_options[key] = file_options.get(key)

        return completed_options
