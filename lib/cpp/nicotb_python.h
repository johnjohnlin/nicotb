#pragma once
#include <glog/logging.h>
#include <numpy/arrayobject.h>
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>
#include <unordered_map>

namespace Nicotb {

typedef std::unordered_map<std::string, size_t> EventEntry;
struct SignalEntry {
	NPY_TYPES t;
	std::vector<int> d;
};
typedef std::unordered_map<std::string, std::pair<
	size_t,
	std::vector<SignalEntry>
>> BusEntry;

namespace Python {

void Init(const EventEntry &e, const BusEntry &s);
void TriggerEvent(size_t i);
// VPI must implement these functions
void ReadSignal(const size_t i, PyObject *npa_list);
void WriteSignal(const size_t i, PyObject *npa_list);

} // namespace Python
} // namespace Nicotb

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
