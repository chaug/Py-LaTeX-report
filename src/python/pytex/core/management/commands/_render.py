from pytex.core.management.base              import NoArgsCommand
from pytex.core.management.commands._project import projectEngine

class RenderCommand(NoArgsCommand):

    def createEngine(self, **options):
        return projectEngine(self, ".", **options)
