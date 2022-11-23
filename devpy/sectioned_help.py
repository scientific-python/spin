import click
import collections


class SectionedHelpGroup(click.Group):
    """Organize commands as sections"""

    def __init__(self, *args, **kwargs):
        self.section_commands = collections.defaultdict(list)
        super().__init__(*args, **kwargs)

    def add_command(self, cmd, name=None, section=None):
        self.section_commands[section].append(cmd)
        super().add_command(cmd, name=name)

    def format_commands(self, ctx, formatter):
        for group, cmds in self.section_commands.items():
            with formatter.section(group):
                formatter.write_dl(
                    [(cmd.name, cmd.get_short_help_str() or "") for cmd in cmds]
                )
