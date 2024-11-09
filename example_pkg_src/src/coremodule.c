#define PY_SSIZE_T_CLEAN
#include <Python.h>

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

static PyMethodDef CoreMethods[] = {
    {"echo",  core_echo, METH_VARARGS, "Echo a string and return 42"},
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
