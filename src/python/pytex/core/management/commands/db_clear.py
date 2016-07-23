from pytex.core.management.commands._render import RenderCommand

class Command(RenderCommand):

    help = ("Clear Database Cache")

    def handle_noargs(self, **options):
        engine = self.createEngine(**options)

        return ""
