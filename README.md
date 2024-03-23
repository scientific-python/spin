# 💫 Scientific Python INcantations (`spin`)

## A developer tool for scientific Python libraries

Developers need to memorize a whole bunch of magic command-line incantations.
And these incantations change from time to time!
Typically, their lives are made simpler by a Makefile, but Makefiles can be convoluted, are not written in Python, and are hard to extend.
The rationale behind `spin` is therefore to provide a simple interface for common development tasks.
It comes with a few common build commands out the box, but can easily be customized per project.

As a curiosity: the impetus behind developing the tool was the mass migration of scientific Python libraries (SciPy, scikit-image, and NumPy, etc.) to Meson, after distutils was deprecated.
When many of the build and installation commands changed, it made sense to abstract away the nuisance of having to re-learn them.

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
  build  🔧 Build package with Meson/ninja and install
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
  build    🔧 Build package with Meson/ninja and install to `build-install`
  ipython  💻 Launch IPython shell with PYTHONPATH set
  python   🐍 Launch Python shell with PYTHONPATH set
  shell    💻 Launch shell with PYTHONPATH set
  test     🔧 Run pytest
  run      🏁 Run a shell command with PYTHONPATH set
  docs     📖 Build Sphinx documentation
  gdb      👾 Execute a Python snippet with GDB
  lldb     👾 Execute a Python snippet with LLDB
  install  💽 Build and install package using pip.
```

### [Build](https://pypa-build.readthedocs.io/en/stable/) (PEP 517 builder)

Available as `spin.cmds.build.*`:

```
  sdist    📦 Build a source distribution in `dist/`
```

### [pip](https://pip.pypa.io) (Package Installer for Python)

`pip` allows for editable installs, another common
development workflow.

Note that, for now, the meson commands above do not work with an
editable install of the package. We're [working on changing that](https://github.com/scientific-python/spin/pull/141).

Available as `spin.cmds.pip.*`:

```
  install  💽 Build and install package using pip.
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
both click options and keywords:

```toml
[tool.spin.kwargs]
".spin/cmds.py:example" = {"test" = "default override", "default_kwd" = 3}
```

### Advanced: adding arguments to built-in commands

Instead of rewriting a command from scratch, a project may want to add a flag to a built-in `spin` command, or perhaps do some pre- or post-processing.
For this, we have to use an internal Click concept called a [context](https://click.palletsprojects.com/en/8.1.x/complex/#contexts).
Fortunately, we don't need to know anything about contexts other than that they allow us to execute commands within commands.

We proceed by duplicating the function header of the existing command, and adding our own flag:

```python
from spin.cmds import meson

# Take this from the built-in implementation, in `spin.cmds.meson.build`:


@click.command()
@click.argument("meson_args", nargs=-1)
@click.option("-j", "--jobs", help="Number of parallel tasks to launch", type=int)
@click.option("--clean", is_flag=True, help="Clean build directory before build")
@click.option(
    "-v", "--verbose", is_flag=True, help="Print all build output, even installation"
)

# This is our new option
@click.option("--custom-arg/--no-custom-arg")

# This tells spin that we will need a context, which we
# can use to invoke the built-in command
@click.pass_context

# This is the original function signature, plus our new flag
def build(ctx, meson_args, jobs=None, clean=False, verbose=False, custom_arg=False):
    """Docstring goes here. You may want to copy and customize the original."""

    # Do something with the new option
    print("The value of custom arg is:", custom_arg)

    # The spin `build` command doesn't know anything about `custom_arg`,
    # so don't send it on.
    del ctx.params["custom_arg"]

    # Call the built-in `build` command, passing along
    # all arguments and options.
    ctx.forward(meson.build)

    # Also see:
    # - https://click.palletsprojects.com/en/8.1.x/api/#click.Context.forward
    # - https://click.palletsprojects.com/en/8.1.x/api/#click.Context.invoke
```

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
nox -s tests
```

## History

The `dev.py` tool was [proposed for SciPy](https://github.com/scipy/scipy/issues/15489) by Ralf Gommers and [implemented](https://github.com/scipy/scipy/pull/15959) by Sayantika Banik, Eduardo Naufel Schettino, and Ralf Gommers (also see [Sayantika's blog post](https://labs.quansight.org/blog/the-evolution-of-the-scipy-developer-cli)).
Inspired by that implementation, `spin` (this package) is a minimal rewrite by Stéfan van der Walt, that aims to be easily extendable so that it can be used across ecosystem libraries.
We thank Danila Bredikhin and Luca Marconato who kindly donated the `spin` name on PyPi.
