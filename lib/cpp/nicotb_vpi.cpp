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

static void ReadConfig(EventEntry &e, SignalEntry &s)
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
	const char *topm = GetEnv("TOPMODULE");
	for (auto&& e: config.events()) {
		const string &name = e.name();
		auto ev_hier_cs = ToCharUqPtr(string() + topm + '.' + e.ev_hier());
		auto ev_name_cs = ToCharUqPtr(e.ev_name());
		LOG(INFO) << "Name: " << name << ", event = " << ev_hier_cs.get() << '.' << ev_name_cs.get();
		vpiHandle h = VpiHandleByName(ev_hier_cs.get(), nullptr),
		          s = VpiHandleByName(ev_name_cs.get(), h);
	}
}

static PLI_INT32 VpiInitAll(PLI_BYTE8 *args)
{
	InitGoogleLogging("nicotb");
	EventEntry e;
	SignalEntry s;
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
