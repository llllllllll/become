#include <Python.h>

#include "libpy/automethod.h"
#include "libpy/libpy.h"

static py::object become_impl(py::object,
                              PyObject *ob,
                              py::object to_become,
                              py::list::object ranges) {

    if (!(Py_TYPE(ob)->tp_flags & Py_TPFLAGS_HEAPTYPE) ||
        !(Py_TYPE(to_become)->tp_flags & Py_TPFLAGS_HEAPTYPE)) {
        PyErr_SetString(PyExc_TypeError,
                        "cannot use 'become' with non-heaptypes");
        return nullptr;
    }

    // Track the number of places where ``ob`` became ``to_become``.
    py::ssize_t changed = 0;

    // we need to store this in a register because as we are iterating over our
    // pages will mutate the stack which will alter the value of ``ob``. This
    // hides the value from our loop below.
    // r12 is used because x86 does not use this register for calling functions.
    register PyObject *ob_register asm("r12") = ob;

    for (const py::tuple::object &slice : ranges) {
        py::ssize_t len(slice.len());

        if (len != 2) {
            // if we find a non-tuple in the list, len() will return -1 and set
            // and error
            if (!PyErr_Occurred()) {
                // if no error was raised, we just got a tuple with a different
                // len, set an assertion error.
                PyErr_Format(PyExc_AssertionError,
                             "expected tuples of length 2, got: %zd",
                             len);
            }

            return nullptr;
        }

        py::long_::object start(slice[0]);
        py::long_::object stop(slice[1]);

        if (!start.is_nonnull() || !stop.is_nonnull()) {
            return nullptr;
        }

        for (PyObject **p = reinterpret_cast<PyObject**>(start.as_size_t());
             p < reinterpret_cast<PyObject**>(stop.as_size_t());
             ++p) {
            if (*p == ob_register) {
                ++changed;
                *p = to_become;
            }
        }
    }

    // move all the references from ``ob_register`` to ``to_become`` because
    // anyone that was referring to ``ob_register`` now actually owns a ref
    // of ``to_become``.
    Py_REFCNT(to_become) += Py_REFCNT(ob_register);

    if (Py_TYPE(ob_register)->tp_flags & Py_TPFLAGS_HAVE_GC) {
        PyObject_GC_UnTrack(ob_register);
        PyObject_GC_Del(ob_register);
    }
    else {
        PyObject_Del(ob_register);
    }

    return py::long_::object(changed);
}

PyMethodDef methods[] = {
    automethod(become_impl),
    {NULL},
};

static struct PyModuleDef _become_module = {
    PyModuleDef_HEAD_INIT,
    "become._become",
    "",
    -1,
    methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
PyInit__become(void)
{
    return PyModule_Create(&_become_module);
}
