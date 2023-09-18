set -e

RED="\033[31;1m"
MAGENTA="\033[35m"
NORMAL="\033[0m"

prun() { echo -e "\n$RED\$ $@ $NORMAL\n" ; "$@" ; }

prun cd example_pkg

prun spin build

# Test spin run
SPIN_PYTHONPATH=$(spin run 'echo $PYTHONPATH')
echo spin sees PYTHONPATH=\"${SPIN_PYTHONPATH}\"
if [[ ${SPIN_PYTHONPATH} == "\$PYTHONPATH" ]]; then
    echo "Expected Python path, but got $SPIN_PYTHONPATH instead"
    exit 1
fi
echo -e "${MAGENTA}Does \$PYTHONPATH contains site-packages?${NORMAL}"
if [[ ${SPIN_PYTHONPATH} == *"site-packages" ]]; then
    echo "Yes"
else
    echo "No; it is $SPIN_PYTHONPATH"
fi
echo -e "${MAGENTA}Does \`spin run\` redirect only command output to stdout?${NORMAL}"
# Once we're on Python >3.11, can replace syspath manipulation below with -P flag to Python
VERSION=$(spin run python -c 'import sys; del sys.path[0]; import example_pkg; print(example_pkg.__version__)')
if [[ $VERSION == "0.0.0dev0" ]]; then
    echo "Yes"
else
    echo "No, output is $VERSION"
    exit 1
fi

prun spin test
echo -e "${MAGENTA}Running \`spin test\`, but with PYTHONPATH set${NORMAL}"
PYTHONPATH=./tmp spin test

prun spin sdist
prun spin example
prun spin docs
