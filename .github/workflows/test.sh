set -e

prun() { echo "\$ $@" ; "$@" ; }

prun cd example_pkg

prun spin build
prun spin test
prun spin sdist
prun spin example
prun spin docs

SPIN_PYTHONPATH=$(spin run 'echo $PYTHONPATH')
echo spin sees PYTHONPATH=\"${SPIN_PYTHONPATH}\"
$ if [[ ${SPIN_PYTHONPATH} == "\$PYTHONPATH" ]]; then
    echo -n "\!\!\!\!\n\nIf this says \$PYTHONPATH, that's an error\n\n\!\!\!\!\n"
fi
[[ ${SPIN_PYTHONPATH} == *"site-packages" ]]

prun spin run python -c 'import sys; del sys.path[0]; import example_pkg; print(example_pkg.__version__)'
