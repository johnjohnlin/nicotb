NICOTB=/home/ta/nicotb/lib
IRUN=/opt/CAD/INCISIV/cur/tools.lnx86/bin/64bit/irun

%: %.sv
	GLOG_logtostderr=1 \
	TEST=$(if $(TEST),$(TEST),$@) \
	TOPMODULE=$(if $(TOPMODULE),$(TOPMODULE),$@) \
	CONNECT_CONFIG=$(if $(CONNECT_CONFIG),$(CONNECT_CONFIG),$@).txt \
	PYTHONPATH=$(NICOTB)/python:`pwd` \
	$(IRUN) +access+rw -loadvpi $(NICOTB)/cpp/nicotb.so:VpiBoot -incdir $(NICOTB)/verilog $<


