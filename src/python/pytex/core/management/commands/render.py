from pytex.core.management.commands._render import RenderCommand

class Command(RenderCommand):

    help = ("Render LaTeX sources")

    def handle_noargs(self, **options):
        engine  = self.createEngine(**options)
        project = engine.createProject()

        engine.scafold(project)
        return ""
