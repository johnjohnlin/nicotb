NICOTB=~/nicotb/lib
IRUN=/opt/CAD/INCISIV/cur/tools.lnx86/bin/64bit/irun

%: %.sv
	GLOG_logtostderr=1 \
	TEST=$(if $(TEST),$(TEST),$@) \
	TOPMODULE=$(if $(TOPMODULE),$(TOPMODULE),$@) \
	PYTHONPATH=$(NICOTB)/python:`pwd` \
	$(IRUN) +access+rw -loadvpi $(NICOTB)/cpp/nicotb.so:VpiBoot $(NICOTB)/verilog/Utils.sv $<

