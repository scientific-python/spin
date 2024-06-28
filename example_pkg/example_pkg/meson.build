py.extension_module(
  '_core',
  'coremodule.c',
  install: true,
  subdir: 'example_pkg'
)

python_sources = [
  '__init__.py',
  'conftest.py'
]

py.install_sources(
  python_sources,
  subdir: 'example_pkg'
)

install_subdir('submodule', install_dir: py.get_install_dir() / 'example_pkg')
install_subdir('tests', install_dir: py.get_install_dir() / 'example_pkg')
