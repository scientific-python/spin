# 💫 Scientific Python INcantations (`spin`)

## A developer tool for scientific Python libraries

Developers need to memorize a whole bunch of magic command-line incantations.
These incantations may also change over time.
Often, Makefiles are used to provide aliases, but Makefiles can be convoluted, are not written in Python, and are hard to extend.
The goal of `spin` is therefore to provide a simple, user-friendly, extendable interface for common development tasks.
It comes with a few common build commands out the box, but can easily be customized per project.

As a curiosity: the impetus behind developing the tool was the mass migration of scientific Python libraries (SciPy, scikit-image, and NumPy, etc.) to Meson, after distutils was deprecated.
When many of the build and installation commands changed, it made sense to abstract away the nuisance of having to re-learn them.

_Note:_ We now have experimental builds for editable installs.
Most of the Meson commands listed below should work "out of the box" for those.

<!--TOC-->

- [Installation](#installation)
- [Configuration](#configuration)
  - [Command sections](#command-sections)
- [Running](#running)
- [Built-in commands](#built-in-commands)
  - [Meson](#meson)
  - [Build (PEP 517 builder)](#build-pep-517-builder)
  - [pip (Package Installer for Python)](#pip-package-installer-for-python)
  - [Meta (commands that operate on commands)](#meta-commands-that-operate-on-commands)
- [🧪 Custom commands](#-custom-commands)
  - [Configuration](#configuration-1)
  - [Argument overrides](#argument-overrides)
  - [Advanced: adding arguments to built-in commands](#advanced-adding-arguments-to-built-in-commands)
  - [Advanced: override Meson CLI](#advanced-override-meson-cli)
- [FAQ](#faq)
- [For contributors](#for-contributors)
- [History](#history)

<!--TOC-->

## Installation

```
pip install spin
```

## Configuration

Settings are stored in `.spin.toml`, `spin.toml`, or your project's `pyproject.toml`.
As an example, see the `[tool.spin]` section of [an example `pyproject.toml`](https://github.com/scientific-python/spin/blob/main/example_pkg/pyproject.toml).

The `[project]` section should contain `name`.
The `[tool.spin]` section should contain:

```
package = "pkg_importname"  # name of your package
commands = [
  "spin.cmds.meson.build",
  "spin.cmds.meson.test"
]
```

See [the command selection](#built-in-commands) below.

### Command sections

Once you have several commands, it may be useful to organize them into sections.
In `pyproject.toml`, instead of specifying the commands as a list, use the following structure:

```toml
[tool.spin.commands]
"Build" = [
  "spin.cmds.meson.build",
  "spin.cmds.meson.test"
]
"Environments" = [
  "spin.cmds.meson.ipython",
  "spin.cmds.meson.run"
]
```

These commands will then be rendered as:

```
Build:
  build  🔧 Build package with Meson/ninja
  test   🔧 Run tests

Environments:
  ipython  💻 Launch IPython shell with PYTHONPATH set
  run      🏁 Run a shell command with PYTHONPATH set
```

## Running

```
spin
```

or

```
python -m spin
```

## Built-in commands

### [Meson](https://meson-python.readthedocs.io)

Available as `spin.cmds.meson.*`.

```
build      🔧 Build package with Meson/ninja
ipython    💻 Launch IPython shell with PYTHONPATH set
python     🐍 Launch Python shell with PYTHONPATH set
shell      💻 Launch shell with PYTHONPATH set
test       🔧 Run pytest
run        🏁 Run a shell command with PYTHONPATH set
docs       📖 Build Sphinx documentation
gdb        👾 Execute a Python snippet with GDB
lldb       👾 Execute a Python snippet with LLDB
```

### [Build](https://pypa-build.readthedocs.io/en/stable/) (PEP 517 builder)

Available as `spin.cmds.build.*`:

```
sdist      📦 Build a source distribution in `dist/`
```

### [pip](https://pip.pypa.io) (Package Installer for Python)

`pip` allows for editable installs, another common
development workflow.

Available as `spin.cmds.pip.*`:

```
install    💽 Build and install package using pip.
```

### Meta (commands that operate on commands)

Available as `spin.cmds.meta.*`:

```
introspect 🔍 Print a command's location and source code
```

## 🧪 Custom commands

`spin` can invoke custom commands. These commands define their own arguments, and have access to the `pyproject.toml` file for further configuration.

See, e.g., the [example custom command](https://github.com/scientific-python/spin/blob/main/example_pkg/.spin/cmds.py).

Add custom commands to the `commands` variable in the `[tool.spin]` section of `pyproject.toml` as follows:

```
commands = [..., '.spin/cmds.py:example']
```

Here, the command is stored in `.spin/cmds.py`, and the function
is named `example`.

### Configuration

Custom commands can access the `pyproject.toml` as follows:

```python
from spin import util


@click.command()
def example():
    """Command that accesses `pyproject.toml` configuration"""
    config = util.get_config()
    print(config["tool.spin"])
```

### Argument overrides

Default arguments can be overridden for any command.
The custom command above, e.g., has the following signature:

```python
@click.command()
@click.option("-f", "--flag")
@click.option("-t", "--test", default="not set")
def example(flag, test, default_kwd=None):
    """🧪 Example custom command.
    ...
    """
```

Use the `[tool.spin.kwargs]` section to override default values for
click options or function keywords:

```toml
[tool.spin.kwargs]
".spin/cmds.py:example" = {"test" = "default override", "default_kwd" = 3}
```

### Advanced: adding arguments to built-in commands

Instead of rewriting a command from scratch, a project may simply want to add a flag to an existing `spin` command, or perhaps do some pre- or post-processing.
For this purpose, we provide the `spin.util.extend_cmd` decorator.

Here, we show how to add a `--extra` flag to the existing `build` function:

```python
import spin


@click.option("-e", "--extra", help="Extra test flag")
@spin.util.extend_command(spin.cmds.meson.build)
def build_extend(*, parent_callback, extra=None, **kwargs):
    """
    This version of build also provides the EXTRA flag, that can be used
    to specify an extra integer argument.
    """
    print(f"Preparing for build with {extra=}")
    parent_callback(**kwargs)
    print("Finalizing build...")
```

Note that `build_extend` receives the parent command callback (the function the `build` command would have executed) as its first argument.

The matching entry in `pyproject.toml` is:

```
"Build" = [".spin/cmds.py:build_extend"]
```

The `extend_cmd` decorator also accepts a `doc` argument, for setting the new command's `--help` description.
The function documentation ("This version of build...") is also appended.

Finally, `remove_args` is a tuple of arguments that are not inherited from the original command.

### Advanced: override Meson CLI

Some packages use a vendored version of Meson. The path to a custom
Meson CLI can be set in `pyproject.toml`:

```
[tool.spin.meson]
cli = 'path/to/custom/meson'
```

## FAQ

- Running `spin`, the emojis in the command list don't show up.

Your terminal font may not include emoji characters. E.g., if you use
noto on Arch Linux the emojis are installed separately:

```sh
sudo pacman -S noto-fonts-emoji
fc-cache -f -v
```

## For contributors

`spin` development happens on GitHub at [scientific-python/spin](https://github.com/scientific-python/spin).
`spin` tests are invoked using:

```
nox -s test
```

Other examples:

```
nox -s test -- -v
nox -s test -- -v spin/tests/test_meson.py
```

## History

The `dev.py` tool was [proposed for SciPy](https://github.com/scipy/scipy/issues/15489) by Ralf Gommers and [implemented](https://github.com/scipy/scipy/pull/15959) by Sayantika Banik, Eduardo Naufel Schettino, and Ralf Gommers (also see [Sayantika's blog post](https://labs.quansight.org/blog/the-evolution-of-the-scipy-developer-cli)).
Inspired by that implementation, `spin` (this package) is a minimal rewrite by Stéfan van der Walt, that aims to be easily extendable so that it can be used across ecosystem libraries.
We thank Danila Bredikhin and Luca Marconato who kindly donated the `spin` name on PyPi.
