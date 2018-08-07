PY=python
CFLAGS=$(shell $(PY)-config --cflags) -fPIC --std=c++11 -c \
       -I$(shell $(PY) -c "from numpy import get_include as i; print(i())") \
       -DNDEBUG -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
LDFLAGS=$(shell $(PY)-config --ldflags) -lglog -shared

.PHONY : clean verilator_c vpi

all: verilator_c vpi

verilator_c: nicotb_verilator.o nicotb_python.o
	g++ $^ $(LDFLAGS) -o nicotb_verilator_c.so

vpi: nicotb_vpi.o nicotb_python.o
	g++ $^ $(LDFLAGS) -o nicotb.so

nicotb_python.o: nicotb_python.cpp nicotb_python.h
	g++ $(CFLAGS) $<

nicotb_verilator.o: nicotb_verilator.cpp nicotb_python.h nicotb_verilator.h
	g++ $(CFLAGS) $<

nicotb_vpi.o: nicotb_vpi.cpp nicotb_python.h
	g++ $(CFLAGS) $<

clean:
	rm *.o *.so
