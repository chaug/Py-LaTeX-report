from pytex.core.management.commands._project import ProjectCommand

class Command(ProjectCommand):

    help  = "Generate a project from a template"

    def handle_project(self, project_folder, **options):
        engine = self.createEngine(project_folder, **options)
        engine.copy_templates()
        return ""
