from optparse import make_option

from pytex.core.management.base               import BaseCommand, CommandError
from pytex.core.management.commands._settings import ProjectSettings

from pytex.core.engines.scafold_engine        import Engine

def getTemplateList():
    return Engine.templates()

def projectEngine(command, project_folder, writable = False, **options0):
    project_settings = ProjectSettings(project_folder, ["template"])
    options = project_settings.createAndComplete(**options0)
    command.log(2, "PROJECT_ROOT: %s" % project_settings.root)
    command.log(2, "    TEMPLATE: %s" % options.get("template"))

    engine = Engine(
        command,
        project_root=project_settings.root,
        **options
    )
    if not engine.validate_template():
        raise CommandError("Template %s doesn't exist." % engine.template)

    return engine


class ProjectCommand(BaseCommand):

    args  = '<PROJECT_FOLDER*>'
    label = 'PROJECT_FOLDER'

    option_list = BaseCommand.option_list + (
        make_option('--template', '-t', action='store', dest='template',
            help='Template from (%s).' % ",".join(getTemplateList()),
        ),
    )

    def handle(self, *labels, **options):
        project_folders = labels or ["."]

        output = []
        for project_folder in project_folders:
            sub_output = self.handle_project(project_folder, **options)
            if sub_output:
                output.append(sub_output)
        return '\n'.join(output)

    def createEngine(self, project_folder, **options):
        return projectEngine(self, project_folder, writable=True, **options)
