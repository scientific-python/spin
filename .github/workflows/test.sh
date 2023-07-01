set -xe

cd example_pkg

spin build
spin test
spin sdist
spin example
spin docs

[[ $(spin run 'echo $PYTHONPATH') != '$PYTHONPATH' ]]

spin run python -c 'import sys; del sys.path[0]; import example_pkg; print(example_pkg.__version__)'
