NICOTB=~/nicotb/lib
IRUN=/opt/CAD/INCISIV/cur/tools.lnx86/bin/64bit/irun

%: %.sv
	GLOG_logtostderr=1 \
	TEST=$(if $(TEST),$(TEST),$@) \
	TOPMODULE=$(if $(TOPMODULE),$(TOPMODULE),$@) \
	PYTHONPATH=$(NICOTB)/python:`pwd` \
	$(IRUN) +access+rw -loadvpi $(NICOTB)/cpp/nicotb.so:VpiBoot $(NICOTB)/verilog/Utils.sv $<

dump_scoreboard:
	@echo -e \
	".open scoreboard.db\n"\
	".header on\n"\
	".mode column\n"\
	".print ===============\n"\
	".print All Scoreboards\n"\
	".print ===============\n"\
	"select * from Scoreboard;\n"\
	".print\n"\
	".print =========\n"\
	".print All Tests\n"\
	".print =========\n"\
	"select * from Tests;\n"\
	 | sqlite3
