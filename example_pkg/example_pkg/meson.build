subdir('submodule')

py.extension_module(
  '_core',
  'coremodule.c',
  include_directories: 'submodule',
  dependencies: shlib_dep,
  install: true,
  subdir: 'example_pkg',
  install_rpath: '$ORIGIN/submodule',
)

python_sources = [
  '__init__.py',
  'conftest.py'
]

py.install_sources(
  python_sources,
  subdir: 'example_pkg'
)

install_subdir('tests', install_dir: py.get_install_dir() / 'example_pkg')
