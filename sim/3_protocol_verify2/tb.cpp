#include <memory>
#include <iostream>
#include <algorithm>
#include "Vdut.h"
#include "verilated_vcd_c.h"
#include "nicotb_verilator.h"

int main()
{
	using namespace std;
	namespace NiVe = Nicotb::Verilator;
	constexpr int MAX_SIM_CYCLE = 1000;
	constexpr int SIM_CYCLE_AFTER_STOP = 10;
	int n_sim_cycle = MAX_SIM_CYCLE, ret = 0;
	auto dump_name = "tb.vcd";
	typedef Vdut TopType;

	// Init dut and signals
	// TOP is the default name of our macro
	unique_ptr<TopType> TOP(new TopType);
	TOP->eval();
	MAP_SIGNAL(irdy);
	MAP_SIGNAL(iack);
	MAP_SIGNAL(iint);
	MAP_SIGNAL(ordy);
	MAP_SIGNAL(ocanack);
	MAP_SIGNAL(oint);

	// Init events
	NiVe::AddEvent("ck_ev");
	NiVe::AddEvent("rst_out");

	// Init simulation
	vluint64_t sim_time = 0;
	unique_ptr<VerilatedVcdC> tfp(new VerilatedVcdC);
	Verilated::traceEverOn(true);
	TOP->trace(tfp.get(), 99);
	tfp->open ("tb.vcd");

	// Simulation
#define Eval TOP->eval();NiVe::UpdateWrite();tfp->dump(sim_time++)
	NiVe::Init();
	const size_t ck_ev = NiVe::GetEventIdx("ck_ev"),
	             rst_out = NiVe::GetEventIdx("rst_out");
	TOP->clk = 0;
	TOP->rst = 1;
	Eval;
	TOP->rst = 0;
	Eval;
	TOP->rst = 1;
	NiVe::TriggerEvent(rst_out);
	Eval;
	int cycle = 0;
	for (
			;
			cycle < n_sim_cycle and not Verilated::gotFinish();
			++cycle
	) {
		TOP->clk = 1;
		NiVe::TriggerEvent(ck_ev);
		Eval;
		TOP->clk = 0;
		Eval;
		if (Nicotb::nicotb_fin_wire) {
			n_sim_cycle = min(cycle + SIM_CYCLE_AFTER_STOP, n_sim_cycle);
		}
	}
	cout << "Simulation stop at timestep " << cycle << endl;
	tfp->close();
	NiVe::Final();
	return 0;
}
