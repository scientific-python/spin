# Developer tool for scientific Python libraries

Developers need to memorize a whole bunch of magic command-line incantations.
And these incantations change from time to time!
Typically, their lives are made simpler by a Makefile, but Makefiles can be convoluted, are not written in Python, and are hard to extend.
The rationale behind `devpy` is therefore to provide a simple interface for common development tasks.
It comes with a few common build commands out the box, but can easily be customized per project.

As a curiosity: the impetus behind developing the tool was the mass migration of scientific Python libraries (SciPy, scikit-image, and NumPy, etc.) to Meson, after distutils was deprecated.
When many of the build and installation commands changed, it made sense to abstract away the nuisance of having to re-learn them.

## Installation

`devpy` is not yet available via PyPi (but soon!).

Meanwhile, please install it directly from GitHub:

```
pip install git+https://github.com/scientific-python/devpy
```

## Configuration

Settings are in your project's `pyproject.toml`.
As an example, see the `[tool.devpy]` section of [an example `pyproject.toml`](https://github.com/scientific-python/devpy/blob/main/example_pkg/pyproject.toml).

The `[tool.devpy]` section should contain:

```
package = 'pkg_importname'  # used by pytest
commands = ['devpy.build', 'devpy.test']
```

## Running

```
python -m devpy
```

On Unix-like systems, you can also copy the [`dev.py` script](https://github.com/scientific-python/devpy/blob/main/example_pkg/dev.py) to the root of your project directory, and launch it as:

```
./dev.py
```

## Built-in commands

```
  build    🔧 Build package with Meson/ninja and install to `build-install`
  ipython  💻 Launch IPython shell with PYTHONPATH set
  python   🐍 Launch Python shell with PYTHONPATH set
  shell    💻 Launch shell with PYTHONPATH set
  test     🔧 Run tests
```

## 🧪 Custom commands

`devpy` can invoke custom commands. These commands define their own arguments, and have access to the `pyproject.toml` file for further configuration.

See, e.g., the [example custom command](https://github.com/scientific-python/devpy/blob/main/example_pkg/.devpy/cmds.py).

Add custom commands to the `commands` variable in the `[tool.devpy]` section of `pyproject.toml` as follows:

```
commands = [..., '.devpy/cmds.py:example']
```

Here, the command is stored in `.devpy/cmds.py`, and the function
is named `example`.

### Configuration

Custom commands can access the `pyproject.toml` as follows:

```python
from devpy import util

@click.command()
def example():
    """Command that accesses `pyproject.toml` configuration"""
    config = util.get_config()
    print(config["tool.devpy"])
```

### Command sections

Once you have several commands, it may be useful to organize them into sections.
In `pyproject.toml`, instead of specifying the commands as a list, use the following structure:

```toml
[tool.devpy.commands]
"Build" = ["devpy.build_meson", "devpy.test"]
"Environments" = ["devpy.shell", "devpy.ipython", "devpy.python"]
```

These commands will then be rendered as:

```
Build:
  build  🔧 Build package with Meson/ninja and install
  test   🔧 Run tests

Environments:
  shell    💻 Launch shell with PYTHONPATH set
  ipython  💻 Launch IPython shell with PYTHONPATH set
  python   🐍 Launch Python shell with PYTHONPATH set
```

## History

The `dev.py` tool was [proposed for SciPy](https://github.com/scipy/scipy/issues/15489) by Ralf Gommers and [implemented](https://github.com/scipy/scipy/pull/15959) by Sayantika Banik, Eduardo Naufel Schettino, and Ralf Gommers (also see [Sayantika's blog post](https://labs.quansight.org/blog/the-evolution-of-the-scipy-developer-cli)).
Inspired by that implementation, `devpy` (this package) is a minimal rewrite by Stéfan van der Walt, that aims to be easily extendable so that it can be used across ecosystem libraries.
