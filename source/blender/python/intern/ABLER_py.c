#include "ABLER_py.h"
#include <Python.h>

#ifdef WIN32
#  include <direct.h>
#else
#  include <unistd.h>
#endif

#define FILE_MAX 1024

static void call_abler_function(wchar_t *w_cwd, char* file_name, char* function_name) {
  PyGILState_STATE gilstate = PyGILState_Ensure();

  PySys_SetPath(w_cwd);
  PyObject *module = NULL, *result = NULL;

  module = PyImport_ImportModule(file_name);
  if (!module) {
    PyGILState_Release(gilstate);
    return;
  }

  result = PyObject_CallMethod(module, function_name, NULL);

  printf("result before ref count: %ld\n", result->ob_refcnt);
  printf("module before ref count: %ld\n", module->ob_refcnt);

  Py_DECREF(result);
  Py_DECREF(module);

  printf("result ref count: %ld\n", result->ob_refcnt);
  printf("module ref count: %ld\n", module->ob_refcnt);

  if (PyErr_Occurred()) {
    PyErr_Print();
  }

  PyGILState_Release(gilstate);
}

#if defined(WIN32)
static void get_directory(wchar_t *dest, wchar_t *w_file_path) {
  _wgetcwd(dest, FILE_MAX);
  wcscat(dest, w_file_path);
}
#else
static void get_directory(wchar_t *dest, char *file_path) {
  char cwd[FILE_MAX];
  getcwd(cwd, sizeof(cwd));
  strcat(cwd, file_path);

  const size_t size = strlen(cwd) + 1;
  mbstowcs(dest, cwd, size);
}
#endif


void tracker_open_fail(void)
{
  wchar_t w_cwd[FILE_MAX];
#if defined(WIN32)
  get_directory(w_cwd, L"\\release\\scripts\\startup\\abler");
#else
  get_directory(w_cwd, "/release/scripts/startup/abler");
#endif

  call_abler_function(
      w_cwd, "tracker_functions", "tracker_file_open_fail");
}


void tracker_open(void)
{
  wchar_t w_cwd[FILE_MAX];
#if defined(WIN32)
  get_directory(w_cwd, L"\\release\\scripts\\startup\\abler");
#else
  get_directory(w_cwd, "/release/scripts/startup/abler");
#endif

  call_abler_function(
      w_cwd, "tracker_functions", "tracker_file_open");
}