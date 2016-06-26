from optparse import make_option

from pytex.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = ("Runs the command-line client.")

    option_list = BaseCommand.option_list + (
        make_option('--template', action='store', dest='template',
            help='Nominates a template onto which to run a shell.'),
    )

    def handle(self, **options):
    	print "SCAFOLD", repr(options)
