from pytex.core.management.commands._render import RenderCommand

class Command(RenderCommand):

    help = ("Render and Load Data from Database")

    def handle_noargs(self, **options):
        engine = self.createEngine(**options)

        return ""
