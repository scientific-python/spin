# Developer tool for scientific Python libraries

Developers need to memorize a whole bunch of magic command-line incantations.
And these incantations change from time to time!
Typically, their lives are made simpler by a Makefile, but Makefiles can be convoluted, are not written in Python, and are hard to extend.
The rationale behind `devpy` is therefore to provide a simple interface for common development tasks.
It comes with a few common build commands out the box, but can easily be customized per project.

As a curiosity: the impetus behind developing the tool was the mass migration of scientific Python libraries (SciPy, scikit-image, and NumPy, etc.) to Meson, after distutils was deprecated.
When many of the build and installation commands changed, it made sense to abstract away the nuisance of having to re-learn them.

## Configuration

Settings are in your project's `pyproject.toml`.
As an example, see the `[tool.devpy]` section of [this project's `pyproject.toml`](https://github.com/scientific-python/devpy/blob/main/pyproject.toml).

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
  build    🔧 Build package with Meson/ninja
  ipython  💻 Launch IPython shell with PYTHONPATH set
  python   🐍 Launch Python shell with PYTHONPATH set
  shell    💻 Launch shell with PYTHONPATH set
  test     🔧 Run tests
```

## 🧪 Custom commands

`devpy` can invoke custom commands. These commands define their own arguments, and they also have access to the `pyproject.toml` file for further configuration.

See, e.g., the [example custom command](https://github.com/scientific-python/devpy/blob/main/custom/__init__.py).

Add custom commands to the `commands` variable in the `[tool.devpy]` section of `pyproject.toml` as follows:

```
commands = [..., 'custom/__init__.py:example']
```

Here, the command is stored in `custom/__init__.py`, and the function
is named `example`.
