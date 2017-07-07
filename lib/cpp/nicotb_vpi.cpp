#include "vpi_user.h"
#include "nicotb_python.h"
#include "nicotb_config.pb.h"
#include <fstream>
#include <google/protobuf/text_format.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>

namespace Nicotb {

using namespace std;
static vector<vector<vpiHandle>> registered_handles;

namespace Python {

void ReadSignalExt(const size_t i, PyObject *value_list, PyObject *xxx_list) {}
void WriteSignalExt(const size_t i, PyObject *value_list, PyObject *xxx_list) {}

} // namespace Python

namespace Vpi {

using namespace google;
using namespace google::protobuf;

static inline vpiHandle HandleByName(char *hier, vpiHandle h)
{
	vpiHandle ret = vpi_handle_by_name(hier, h);
	LOG_IF(FATAL, not ret) << "Cannot find" << hier;
	LOG(INFO) << "Found vpiHandle " << ret << " from " << hier << " of vpiHandle " << h;
	return ret;
}

static void ExtractSignal(vector<vpiHandle> &handles, const vector<int> &d, const string &hier)
{
	auto hier_cs = ToCharUqPtr(hier);
	vector<vpiHandle> src, dst;
	src.push_back(vpi_handle_by_name(hier_cs.get(), nullptr));
	if (src.back()) {
		LOG(INFO) << hier << " founded: " << src.back();
	} else {
		LOG(FATAL) << hier << " not founded.";
	}
	for (int l: d) {
		dst.clear();
		for (auto &&h: src) {
			for (int i = 0; i < l; ++i) {
				dst.push_back(vpi_handle_by_index(h, i));
				if (dst.back()) {
					LOG(INFO) << "Index " << i << " of " << h << " found: " << dst.back();
				} else {
					LOG(FATAL) << "Index " << i << " of " << h << " not found.";
				}
			}
		}
		swap(src, dst);
	}
	handles.insert(handles.end(), src.begin(), src.end());
}

static void ReadConfig(EventEntry &eent, BusEntry &bent)
{
	// read protobuf
	const char *cfg_file = GetEnv("CONNECT_CONFIG");

	ifstream ifs(cfg_file);
	LOG_IF(FATAL, not ifs.is_open()) << cfg_file << " is missing";

	io::IstreamInputStream iifs(&ifs);
	NicotbConfig::NicotbConfig config;
	const bool parse_success = TextFormat::Parse(&iifs, &config);
	LOG_IF(FATAL, not parse_success) << "Cannot parse " << cfg_file;

	ifs.close();

	// get vpi
	const string topm = string(GetEnv("TOPMODULE")) + '.';
	// signal groups
	unordered_map<string, vector<tuple<string, vector<int>, NPY_TYPES>>> siggrp_defs;
	static NPY_TYPES ToNp[] = {
		NPY_BOOL,
		NPY_BOOL, NPY_UBYTE, NPY_USHORT, NPY_UINT,
		NPY_BYTE, NPY_SHORT, NPY_INT
	};
	for (auto &&gd: config.siggrp_defs()) {
		const string &name = gd.name();
		const auto ins_result = siggrp_defs.emplace(name, decltype(siggrp_defs)::mapped_type());
		LOG_IF(ERROR, not ins_result.second) << "Signal group " << name << " is already defined.";
		auto &grp_vec = ins_result.first->second;
		if (ins_result.second) {
			for (auto &&s: gd.sigs()) {
				grp_vec.emplace_back(
					s.name(),
					vector<int>(s.shape().begin(), s.shape().end()),
					ToNp[s.np_type()]
				);
			}
		}
	}

	// buses
	for (auto&& b: config.buses()) {
		const string &name = b.name();
		const string &hier = b.hier();
		auto ins_result = bent.emplace(name, BusEntry::mapped_type());
		LOG_IF(ERROR, not ins_result.second) << "Bus " << name << " is already inserted and thus ignored.";

		ins_result.first->second.first = bent.size() - 1;
		auto &bent_vec = ins_result.first->second.second;
		registered_handles.emplace_back();
		for (auto &&sg: b.sig_grps()) {
			const string &def_name = sg.grp_def_name();
			const string &prefix = sg.prefix();
			auto it = siggrp_defs.find(def_name);
			LOG_IF(FATAL, it == siggrp_defs.end()) << "Cannot find signal group definition " << def_name;
			for (auto &&sig: it->second) {
				SignalEntry bent;
				const string &s_hier = topm + prefix + get<0>(sig);
				bent.t = get<2>(sig);
				bent.d = get<1>(sig);
				ExtractSignal(registered_handles.back(), bent.d, s_hier);
				bent_vec.push_back(move(bent));
			}
		}
		for (auto &&s: b.sigs()) {
			SignalEntry bent;
			const string &s_hier = topm + s.name();
			bent.t = ToNp[s.np_type()];
			bent.d.insert(bent.d.end(), s.shape().begin(), s.shape().end());
			ExtractSignal(registered_handles.back(), bent.d, s_hier);
			bent_vec.push_back(move(bent));
		}
		LOG(INFO) << "There are " << registered_handles.back().size() << " handles in " << name;
	}

	// assign events
	for (auto &&e: config.events()) {
		const string &name = e.name();
		const string &hier = string(topm) + e.hier();
		const auto &ev_bound_buses = e.bound_buses();
		const auto ins_result = eent.emplace(name, EventEntry::mapped_type());
		if (not ins_result.second) {
			LOG(ERROR) << "Signal " << name << " is already inserted and thus ignored.";
			continue;
		}
		auto &target_entry = ins_result.first->second;
		target_entry.first = eent.size() - 1;
		if (e.has_hier()) {
			auto hier_cs = ToCharUqPtr(hier);
			LOG(INFO) << "Name: " << name << ", event = " << hier;
			vpiHandle h = HandleByName(hier_cs.get(), nullptr);
			s_vpi_value v;
			const unsigned writev = target_entry.first;
			v.format = vpiIntVal;
			v.value.integer = writev;
			vpi_put_value(h, &v, NULL, vpiNoDelay);
			LOG(INFO) << "Set signal " << name << " to " << writev;
		}
		for (const string &bidx: ev_bound_buses) {
			auto it = bent.find(bidx);
			LOG_IF(FATAL, it == bent.end()) << "Signal " << bidx << " for " << name << " not found";
			target_entry.second.push_back(it->second.first);
		}
	}
}

static PLI_INT32 Init(PLI_BYTE8 *args)
{
	InitGoogleLogging("nicotb");
	EventEntry e;
	BusEntry b;
	ReadConfig(e, b);
	Python::Init(e, b);
	return 0;
}

static PLI_INT32 TriggerEvent(PLI_BYTE8 *args)
{
	vpiHandle systfref, args_iter, argh;
	struct t_vpi_value argval;
	systfref = vpi_handle(vpiSysTfCall, NULL);
	args_iter = vpi_iterate(vpiArgument, systfref);
	argh = vpi_scan(args_iter);
	argval.format = vpiIntVal;
	vpi_get_value(argh, &argval);
	vpi_free_object(args_iter);
	Python::TriggerEvent(argval.value.integer);
	return 0;
}

} // namespace Vpi
} // namespace Nicotb

extern "C" void VpiBoot()
{
	using namespace Nicotb;
	s_vpi_systf_data tasks[] = {
		{vpiSysTask, vpiSysTask, "$NicotbTriggerEvent", Vpi::TriggerEvent, nullptr, nullptr, nullptr},
		{vpiSysTask, vpiSysTask, "$NicotbInit", Vpi::Init, nullptr, nullptr, nullptr}
	};
	for (auto&& task: tasks) {
		vpi_register_systf(&task);
	}
}
