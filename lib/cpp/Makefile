PY=python
CFLAGS=$(shell $(PY)-config --cflags) -fPIC --std=c++11 -c \
       -DNDEBUG -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
LDFLAGS=$(shell $(PY)-config --ldflags) -lglog -shared

all: nicotb_vpi.o nicotb_python.o
	g++ $^ $(LDFLAGS) -o nicotb.so

nicotb_python.o: nicotb_python.cpp nicotb_python.h
	g++ $(CFLAGS) $<

nicotb_vpi.o: nicotb_vpi.cpp nicotb_python.h
	g++ $(CFLAGS) $<

clean:
	rm *.o *.so
