from pytex.core.management.commands._latex import LaTeXCommand

class Command(LaTeXCommand):

    help = ("Generate a PDF document")

    def handle_noargs(self, **options):
        engine = self.createEngine(**options)

        return ""
