# Developer tool for scientific Python libraries

## Configuration

Settings are in your project's `pyproject.toml`.
As an example, see the `[tool.dev.py]` section of [this project's `pyproject.toml`](https://github.com/scientific-python/dev.py/blob/main/pyproject.toml).

The `[tool.dev.py]` section should contain:

```
package = 'pkg_importname'  # used by pytest
commands = ['dev.py.build', 'dev.py.test']
```

## Running `dev.py`

```
python -m dev.py
```

On Unix-like systems, you can also copy the `dev.py` script to the root of your project directory, and launch it as:

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

`dev.py` can invoke custom commands. These commands define their own arguments, and they also have access to the `pyproject.toml` file for further configuration.

See, e.g., the [example custom command](https://github.com/scientific-python/dev.py/blob/main/custom/__init__.py).

Add custom commands to the `commands` variable in the `[tool.dev.py]` section of `pyproject.toml` as follows:

```
commands = [..., `custom/__init__.py:example`]
```

Here, the command is stored in `custom/__init__.py`, and the function
is named `example`.
