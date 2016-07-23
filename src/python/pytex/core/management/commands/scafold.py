from pytex.core.management.commands._project import ProjectCommand

class Command(ProjectCommand):

    help  = "Scafold a PyTex template (deprecated)"

    def handle_project(self, project_folder, **options):
        engine = self.createEngine(project_folder, **options)
        engine.output      = engine.project_root
        engine.destination = engine.project_root
        engine.dummy_db    = True
        return engine.run(engine.template)
