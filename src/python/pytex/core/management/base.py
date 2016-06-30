import os
import sys

from optparse import make_option, OptionParser
import traceback

import pytex

class CommandError(Exception):
    """
    Exception class indicating a problem while executing a management
    command.

    If this exception is raised during the execution of a management
    command, it will be caught and turned into a nicely-printed error
    message to the appropriate output stream (i.e., stderr); as a
    result, raising this exception (with a sensible description of the
    error) is the preferred way to indicate that something has gone
    wrong in the execution of a command.

    """
    pass


def handle_default_options(options):
    if options.pythonpath:
        sys.path.insert(0, options.pythonpath)


class OutputWrapper(object):
    """
    Wrapper around stdout/stderr
    """
    def __init__(self, out, style_func=None, ending='\n'):
        self._out = out
        self.style_func = None
        if hasattr(out, 'isatty') and out.isatty():
            self.style_func = style_func
        self.ending = ending

    def __getattr__(self, name):
        return getattr(self._out, name)

    def write(self, msg, style_func=None, ending=None):
        ending = ending is None and self.ending or ending
        if ending and not msg.endswith(ending):
            msg += ending
        style_func = [f for f in (style_func, self.style_func, lambda x:x)
                      if f is not None][0]
        self._out.write(str(style_func(msg)))


class BaseCommand(object):

    option_list = (
        make_option('-v', '--verbosity', action='store', dest='verbosity', default='1',
            type='choice', choices=['0', '1', '2', '3'],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output'),
        make_option('--pythonpath',
            help='A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".'),
        make_option('--traceback', action='store_true',
            help='Print traceback on exception'),
    )
    help = ''
    args = ''

    def __init__(self):
        self.verbosity = 1

    def get_version(self):
        return pytex.get_version()

    def usage(self, subcommand):
        """
        Return a brief description of how to use this command, by
        default from the attribute ``self.help``.

        """
        usage = '%%prog %s [options] %s' % (subcommand, self.args)
        if self.help:
            return '%s\n\n%s' % (usage, self.help)
        else:
            return usage

    def create_parser(self, prog_name, subcommand):
        """
        Create and return the ``OptionParser`` which will be used to
        parse the arguments to this command.

        """
        return OptionParser(prog=prog_name,
                            usage=self.usage(subcommand),
                            version=self.get_version(),
                            option_list=self.option_list)

    def print_help(self, prog_name, subcommand):
        """
        Print the help message for this command, derived from
        ``self.usage()``.

        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv):
        """
        Set up any environment changes requested (e.g., Python path),
        then run this command. If the
        command raises a ``CommandError``, intercept it and print it sensibly
        to stderr.
        """
        parser = self.create_parser(argv[0], argv[1])
        options, args = parser.parse_args(argv[2:])
        handle_default_options(options)
        self.verbosity = int(options.verbosity)
        try:
            self.execute(*args, **options.__dict__)
        except Exception as e:
            # self.stderr is not guaranteed to be set here
            stderr = getattr(self, 'stderr', OutputWrapper(sys.stderr))
            if options.traceback:
                stderr.write(traceback.format_exc())
            else:
                stderr.write('%s: %s' % (e.__class__.__name__, e))
            sys.exit(1)

    def execute(self, *args, **options):
        self.stdout = OutputWrapper(options.get('stdout', sys.stdout))
        self.stderr = OutputWrapper(options.get('stderr', sys.stderr))

        try:
            output = self.handle(*args, **options)
            if output:
                self.stdout.write(output)
        finally:
            pass

    def handle(self, *args, **options):
        raise NotImplementedError()

    def log(self, level, msg):
        if level <= self.verbosity:
            (self.stdout if level < 2 else self.stderr).write(
                {
                    0 : "",
                    1 : "+ INFO  + ",
                    2 : "+ TRACE + ",
                    3 : "+ DEBUG + ",
                }[level]
                + msg
            )


class LabelCommand(BaseCommand):
    """
    A management command which takes one or more arbitrary arguments
    (labels) on the command line, and does something with each of
    them.

    Rather than implementing ``handle()``, subclasses must implement
    ``handle_label()``, which will be called once for each label.

    If the arguments should be names of installed applications, use
    ``AppCommand`` instead.

    """
    args = '<label label ...>'
    label = 'label'

    def handle(self, *labels, **options):
        if not labels:
            raise CommandError('Enter at least one %s.' % self.label)

        output = []
        for label in labels:
            label_output = self.handle_label(label, **options)
            if label_output:
                output.append(label_output)
        return '\n'.join(output)

    def handle_label(self, label, **options):
        """
        Perform the command's actions for ``label``, which will be the
        string as given on the command line.

        """
        raise NotImplementedError()


class NoArgsCommand(BaseCommand):
    """
    A command which takes no arguments on the command line.

    Rather than implementing ``handle()``, subclasses must implement
    ``handle_noargs()``; ``handle()`` itself is overridden to ensure
    no arguments are passed to the command.

    Attempting to pass arguments will raise ``CommandError``.

    """
    args = ''

    def handle(self, *args, **options):
        if args:
            raise CommandError("Command doesn't accept any arguments")
        return self.handle_noargs(**options)

    def handle_noargs(self, **options):
        """
        Perform this command's actions.

        """
        raise NotImplementedError()
