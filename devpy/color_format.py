import re

import click


class ColorHelpFormatter(click.formatting.HelpFormatter):
    def write_heading(self, heading):
        super().write_heading(click.style(heading, dim=True))

    def write_dl(self, items):
        default_style = click.style("", bold=True, fg="cyan", reset=False)
        reset_style = click.style("", reset=True)
        style_rules = {
            " [A-Z]+": {"bold": True, "fg": "yellow"},
            r"\-[a-z]{1}(?=[ ,]{1})": {"fg": "green"},
        }
        style_rules = {
            re.compile(expr): format for (expr, format) in style_rules.items()
        }
        for (expr, format) in style_rules.items():
            items = [
                (expr.sub(click.style("\\g<0>", **format) + default_style, key), val)
                for (key, val) in items
            ]
        items = [(default_style + key, reset_style + val) for (key, val) in items]
        super().write_dl(items)

    def write_usage(self, prog, args="", prefix=None):
        super().write_usage(
            click.style(prog, bold=True, fg="white"),
            args,
            prefix=click.style("Usage: ", bold=True, fg="yellow"),
        )
