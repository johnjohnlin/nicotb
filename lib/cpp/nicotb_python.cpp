#include "nicotb_python.h"
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <vector>

namespace Nicotb {
namespace Python {

using namespace std;

static PyObject* PyInit_func();
static vector<PyObject*> events;
static vector<PyObject*> signals;
static PyThreadState *thread_state;

PyObject *InitBridgeModule()
{
	static PyMethodDef nicotb_bridge_methods[] = {
		// {"say_hello", say_hello, METH_VARARGS, ""},
		{nullptr, nullptr, 0, nullptr}
	};
	static PyModuleDef nicotb_bridge_module = {
		PyModuleDef_HEAD_INIT,
		"nicotb_bridge", nullptr, -1,
		nicotb_bridge_methods,
		nullptr, nullptr, nullptr, nullptr
	};
	PyObject *p_bridge_module = PyModule_Create(&nicotb_bridge_module);
	PyObject *p_events = PyList_New(0);
	PyObject *p_event_dic = PyDict_New();
	PyObject *p_signals = PyList_New(0);
	PyObject *p_signal_dic = PyDict_New();
	PyModule_AddObject(p_bridge_module, "events", p_events);
	PyModule_AddObject(p_bridge_module, "event_dict", p_event_dic);
	PyModule_AddObject(p_bridge_module, "signals", p_signals);
	PyModule_AddObject(p_bridge_module, "signal_dict", p_signal_dic);
	return p_bridge_module;
}

void TriggerEvent(size_t i)
{
}

void Init(const EventEntry &e, const BusEntry &s)
{
	PyImport_AppendInittab("nicotb_bridge", InitBridgeModule);
	Py_Initialize();
	// PyEval_InitThreads();
	PyRun_SimpleString("import numpy.core.multiarray");
	PyErr_Print();
	LOG(INFO) << 1;
	_import_array();
	PyErr_Print();

	// import module
	LOG(INFO) << 2;
	PyObject *p_module_name = PyUnicode_FromString(GetEnv("TEST"));
	PyObject *p_module = PyImport_Import(p_module_name);
	PyErr_Print();
	LOG(INFO) << 3;

	thread_state = PyEval_SaveThread();
}

} // namespace Python
} // namespace Nicotb
