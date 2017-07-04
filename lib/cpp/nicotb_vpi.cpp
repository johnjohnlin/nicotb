#include "nicotb.h"
#include "nicotb_config.pb.h"
#include <fstream>
#include <google/protobuf/text_format.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>

namespace Nicotb {

using std::string;
using std::vector;
using std::ifstream;
using namespace google;
using namespace google::protobuf;

static void ExtractSignal(SignalEntry &sent, const string &hier)
{
	auto hier_cs = ToCharUqPtr(hier);
	vector<vpiHandle> handles;
	sent.h.push_back(vpi_handle_by_name(hier_cs.get(), nullptr));
	if (sent.h.back()) {
		LOG(INFO) << hier << " founded: " << sent.h.back();
	} else {
		LOG(FATAL) << hier << " not founded.";
	}
	for (int l: sent.d) {
		handles.clear();
		for (auto &&h: sent.h) {
			for (int i = 0; i < l; ++i) {
				handles.push_back(vpi_handle_by_index(h, i));
				if (handles.back()) {
					LOG(INFO) << "Index " << i << " of " << h << " found: " << handles.back();
				} else {
					LOG(FATAL) << "Index " << i << " of " << h << " not found.";
				}
			}
		}
		swap(sent.h, handles);
		LOG(INFO) << sent.h.size();
	}
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
	// assign signals
	const string topm = string(GetEnv("TOPMODULE")) + '.';
	for (auto &&e: config.events()) {
		const string &name = e.name();
		const string &ev_hier = string(topm) + e.ev_hier();
		const string &ev_name = e.ev_name();
		auto ev_hier_cs = ToCharUqPtr(ev_hier);
		auto ev_name_cs = ToCharUqPtr(ev_name);
		LOG(INFO) << "Name: " << name << ", event = " << ev_hier << '.' << ev_name;
		vpiHandle h = VpiHandleByName(ev_hier_cs.get(), nullptr),
		          s = VpiHandleByName(ev_name_cs.get(), h);
		const auto ins_result = eent.emplace(name, eent.size());
		LOG_IF(ERROR, not ins_result.second) << "Signal " << name << " is already inserted and thus ignored.";
		if (ins_result.second) {
			s_vpi_value v;
			const unsigned writev = ins_result.first->second;
			v.format = vpiIntVal;
			v.value.integer = writev;
			vpi_put_value(s, &v, NULL, vpiNoDelay);
			LOG(INFO) << "Set signal " << name << " to " << writev;
		}
	}

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
		auto &sent_vec = ins_result.first->second.second;
		for (auto &&sg: b.sig_grps()) {
			const string &def_name = sg.grp_def_name();
			const string &prefix = sg.prefix();
			auto it = siggrp_defs.find(def_name);
			LOG_IF(FATAL, it == siggrp_defs.end()) << "Cannot find signal group definition " << def_name;
			for (auto &&sig: it->second) {
				SignalEntry sent;
				const string &s_hier = topm + prefix + get<0>(sig);
				sent.t = get<2>(sig);
				sent.d = get<1>(sig);
				ExtractSignal(sent, s_hier);
				sent_vec.push_back(move(sent));
			}
		}
		for (auto &&s: b.sigs()) {
			SignalEntry sent;
			const string &s_hier = topm + s.name();
			sent.t = ToNp[s.np_type()];
			sent.d.insert(sent.d.end(), s.shape().begin(), s.shape().end());
			ExtractSignal(sent, s_hier);
			sent_vec.push_back(move(sent));
		}
	}
}

static PLI_INT32 VpiInitAll(PLI_BYTE8 *args)
{
	InitGoogleLogging("nicotb");
	EventEntry e;
	BusEntry s;
	ReadConfig(e, s);
	return 0;
}

static PLI_INT32 VpiTriggerEvent(PLI_BYTE8 *args)
{
	return 0;
}

} // namespace Nicotb

extern "C" void VpiBoot()
{
	using namespace Nicotb;
	s_vpi_systf_data tasks[] = {
		{vpiSysTask, vpiSysTask, "$NicotbTriggerEvent", VpiTriggerEvent, nullptr, nullptr, nullptr},
		{vpiSysTask, vpiSysTask, "$NicotbInit", VpiInitAll, nullptr, nullptr, nullptr}
	};
	for (auto&& task: tasks) {
		vpi_register_systf(&task);
	}
}
