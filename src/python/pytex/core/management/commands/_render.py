from optparse import make_option

from pytex.core.management.base              import NoArgsCommand
from pytex.core.management.commands._project import projectEngine

class RenderCommand(NoArgsCommand):

    option_list = NoArgsCommand.option_list + (
        make_option('--dummy-db', action='store_true', dest='dummy_db',
            help='Use Dummy DATA.'),
    )

    def createEngine(self, **options):
        return projectEngine(self, ".", **options)
