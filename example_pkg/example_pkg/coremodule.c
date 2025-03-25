#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "shlib.h"

static PyObject *
core_echo(PyObject *self, PyObject *args)
{
    const char *str;
    PyObject *ret;

    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;

    printf("%s\n", str);

    ret = PyLong_FromLong(42);
    Py_INCREF(ret);
    return ret;
}

static PyObject *
example_sum(PyObject *self, PyObject *args)
{
    int a, b;
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }

    long result = sum(a, b);
    return PyLong_FromLong(result);
}

static PyMethodDef CoreMethods[] = {
    {"echo",  core_echo, METH_VARARGS, "Echo a string and return 42"},
    {"example_sum", example_sum, METH_VARARGS, "Sum up two integers"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef coremodule = {
    PyModuleDef_HEAD_INIT,
    "core",   /* name of module */
    NULL,     /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    CoreMethods
};

PyMODINIT_FUNC
PyInit__core(void)
{
    PyObject *m;

    m = PyModule_Create(&coremodule);
    if (m == NULL)
        return NULL;

    return m;
}
