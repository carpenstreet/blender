//
// Created by 장종원 on 2022/08/30.
//
#include <Python.h>
#include "ABLER_py.h"

#ifdef WIN32
#   include <direct.h>
#else
#   include <unistd.h>
#endif

#define FILE_MAX 1024

// file_path root - blender
static void call_abler_function(char* file_path, char* file_name, char* function_name) {
    const PyGILState_STATE gilstate = PyGILState_Ensure();

    char cwd[FILE_MAX];

#if defined(WIN32)
    wchar_t wText[MAX_PATH];
    _wgetcwd(path, MAX_PATH);
#else
    getcwd(cwd, sizeof(cwd));
    strcat(cwd, file_path);

    const size_t size = strlen(cwd) + 1;
    wchar_t wText[size];
    mbstowcs(wText, cwd, size);
#endif

    PySys_SetPath(wText);

    PyObject *module = NULL, *result = NULL;
    module = PyImport_ImportModule(file_name);
    if (module) {
        result = PyObject_CallMethod(module, function_name, NULL);
    }

    PyErr_Print();

    Py_DECREF(result);
    Py_DECREF(module);

    PyGILState_Release(gilstate);
}

void tracker_open_fail(void) {
    call_abler_function("/release/scripts/startup/abler", "tracker_functions", "tracker_file_open_fail");
}

void tracker_open(void) {
    call_abler_function("/release/scripts/startup/abler", "tracker_functions", "tracker_file_open");
}
