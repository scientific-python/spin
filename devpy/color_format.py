import re
import shutil

import click


class RegexpFormatter:
    def __init__(self, rules, default=None):
        if default is None:
            default = {}
        self.rules = {re.compile(expr): format for (expr, format) in rules.items()}
        self.default_style = click.style("", **default, reset=False)
        self.reset_style = click.style("", reset=True)

    def __call__(self, txt):
        for expr, format in self.rules.items():
            txt = expr.sub(click.style("\\g<0>", **format) + self.default_style, txt)
        txt = self.default_style + txt + self.reset_style
        return txt


class ColorHelpFormatter(click.formatting.HelpFormatter):
    def __init__(self, *args, **kwargs):
        kwargs["width"] = shutil.get_terminal_size()[0]
        super().__init__(*args, **kwargs)

    def write_heading(self, heading):
        super().write_heading(click.style(heading, dim=True))

    def write_dl(self, items):
        """Print definition list"""
        key_fmt = RegexpFormatter(
            {
                " [A-Z]+": {"bold": True, "fg": "yellow"},
                r"\-[a-z]{1}(?=[ ,]{1})": {"fg": "green"},
            },
            default={"bold": True, "fg": "cyan"},
        )
        val_fmt = RegexpFormatter({r"\[default: .*?\]": {"dim": True}})
        items = [(key_fmt(key), val_fmt(val)) for (key, val) in items]
        super().write_dl(items)

    def write_usage(self, prog, args="", prefix=None):
        fmt = RegexpFormatter(
            {r"(?<=\[)[A-Z_]+(?=\])": {"fg": "cyan"}}, default={"bold": True}
        )
        super().write_usage(
            click.style(prog, bold=True, fg="white"),
            click.style(fmt(args), bold=True),
            prefix=click.style("Usage: ", bold=True, fg="yellow"),
        )
