set -e

PLATFORM=$(python -c 'import sys; print(sys.platform)')

RED="\033[31;1m"
MAGENTA="\033[35m"
NORMAL="\033[0m"

ptest() { echo -e "\n${MAGENTA}[TEST] $@${NORMAL}\n" ; }
prun() { echo -e "$RED\$ $@ $NORMAL" ; "$@" ; }

prun cd example_pkg

ptest version command runs
prun spin --version

ptest build command runs
pip install meson-python ninja
prun spin build

ptest Does spin expand \$PYTHONPATH?
SPIN_PYTHONPATH=$(spin run 'echo $PYTHONPATH')
echo spin sees PYTHONPATH=\"${SPIN_PYTHONPATH}\"
if [[ ${SPIN_PYTHONPATH} == "\$PYTHONPATH" ]]; then
    echo "Expected Python path, but got $SPIN_PYTHONPATH instead"
    exit 1
fi

ptest Does \$PYTHONPATH contains site-packages?
if [[ ${SPIN_PYTHONPATH} == *"site-packages" ]]; then
    echo "Yes"
else
    echo "No; it is $SPIN_PYTHONPATH"
fi

ptest Does \`spin run\` redirect only command output to stdout?
# Once we're on Python >3.11, can replace syspath manipulation below with -P flag to Python
VERSION=$(spin run python -c 'import sys; del sys.path[0]; import example_pkg; print(example_pkg.__version__)')
if [[ $VERSION == "0.0.0dev0" ]]; then
    echo "Yes"
else
    echo "No, output is $VERSION"
    exit 1
fi

ptest Does spin detect conflict with editable install?
prun pip install --quiet -e .
OUT=$(spin run ls)
if [[ $OUT == *"Warning! An editable installation"* ]]; then
    echo "Yes"
else
    echo "No"
    exit 1
fi
prun pip uninstall --quiet -y example_pkg

if [[ $PLATFORM == linux || $PLATFORM == darwin ]]; then
    # Detecting whether a file is executable is not that easy on Windows,
    # as it seems to take into consideration whether that file is associated as an executable.
    ptest Does \`spin run foo.py\` warn that \`spin run python foo.py\` is likely intended?
    OUT=$( touch __foo.py && spin run __foo.py || true )
    rm __foo.py
    if [[ $OUT == *"Did you mean to call"* ]]; then
        echo "Yes"
    else
        echo "No, output is: $OUT"
        exit 1
    fi
fi

ptest test command runs
prun spin test

ptest Does \`spin test\` work when PYTHONPATH is set?
PYTHONPATH=./tmp spin test

ptest sdist command runs
prun spin sdist

ptest example command runs
prun spin example

ptest docs command runs
pip install --quiet sphinx
prun spin docs

ptest install command works
prun spin install
(cd /tmp ; [[ $(python -c 'import example_pkg; print(example_pkg.__version__)') == "0.0.0dev0" ]])
prun pip uninstall -y --quiet example_pkg

## Platform specialized tests

if [[ $PLATFORM == linux ]]; then
    ptest gdb command runs on linux
    prun spin gdb -c 'import example_pkg; example_pkg.echo("hi")' -- --eval "run" --batch
fi

# if [[ $PLATFORM == darwin ]]; then

# if [[ $PLATFORM =~ ^win.* ]]; then
