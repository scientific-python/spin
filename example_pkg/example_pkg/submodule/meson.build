# Add a basic shared library, used from the Python extension module
# in ../coremodule.c
if meson.get_compiler('c').get_id() in ['msvc', 'clang-cl', 'intel-cl']
  export_dll_args = ['-DSHLIB_DLL_EXPORTS']
  import_dll_args = ['-DSHLIB_DLL_IMPORTS']
else
  export_dll_args = []
  import_dll_args = []
endif

shlib = shared_library(
  'shlib',
  'shlib.c',
  c_args: export_dll_args,
  install: true,
  install_dir: py.get_install_dir() / 'example_pkg/submodule',
)

shlib_dep = declare_dependency(
  compile_args: import_dll_args,
  link_with: shlib,
)

py.install_sources(
  ['__init__.py'],
  subdir: 'example_pkg/submodule',
)

install_subdir('tests', install_dir: py.get_install_dir() / 'example_pkg/submodule')
