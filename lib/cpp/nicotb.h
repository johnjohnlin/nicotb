#pragma once
#include "vpi_user.h"
// TODO: check whether this header includes NPY_TYPES in all versions?
#include <glog/logging.h>
#include <numpy/ndarraytypes.h>
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>
#include <unordered_map>

namespace Nicotb {

typedef std::unordered_map<std::string, vpiHandle> EventEntry;
typedef std::unordered_map<std::string, std::tuple<
	std::string,            // signal name
	NPY_TYPES,              // numpy type
	std::vector<int>,       // signal dimension
	std::vector<vpiHandle>  // signal handle
>> SignalEntry;

void InitPython(const EventEntry &e, const SignalEntry &s);
void TriggerEvent(PyObject *events, int i);

}

static inline std::unique_ptr<char[]> ToCharUqPtr(const std::string &s)
{
	std::unique_ptr<char[]> cs(new char[s.size()+1]);
	strcpy(cs.get(), s.c_str());
	return cs;
}

static inline const char *GetEnv(const char *name)
{
	using namespace google;
	const char *value = getenv(name);
	LOG_IF(FATAL, value == nullptr) << "Environment variable" << name << " not set";
	return value;
}

static inline vpiHandle VpiHandleByName(char *hier, vpiHandle h)
{
	vpiHandle ret = vpi_handle_by_name(hier, h);
	LOG_IF(FATAL, not ret) << "Cannot find" << hier;
	LOG(INFO) << "Found vpiHandle " << ret << " from " << hier << " of vpiHandle " << h;
	return ret;
}
