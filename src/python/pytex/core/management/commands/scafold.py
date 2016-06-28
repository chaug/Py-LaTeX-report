from optparse import make_option

from pytex.core.management.base import BaseCommand, CommandError

from pytex.core.engines.scafold_engine import Engine

class Command(BaseCommand):
    help = ("Runs the command-line client.")
    args = '<TEMPLATE TEMPLATE ...>'

    option_list = BaseCommand.option_list + (
        make_option('--template-list', action='store_true', dest='template_list',
            help='List available templates.'),
        make_option('--output', '-o', action='store', dest='output',
            help='Output folder.'),
    )

    def handle(self, *labels, **options):
        engine = Engine.create(**options)

        if not engine.validate(labels):
            raise CommandError('Unknown error.')

        output = []
        pre_output = engine.pre_run()
        if pre_output:
            output.append(pre_output)
        for label in labels:
            if not engine.validate_template(label):
                raise CommandError("Template %s doesn't exist." % label)
            label_output = engine.run(label)
            if label_output:
                output.append(label_output)
        return '\n'.join(output)
