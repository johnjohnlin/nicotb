CFLAGS=-fPIC -g -fwrapv -c --std=c++11\
       -I/usr/local/include/python3.6m/\
       -DNDEBUG -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
LDFLAGS=-lpython3.6m -lm -lpthread -ldl -lutil -lprotobuf\
        -Xlinker -export-dynamic -Wl,-O2 -Wl,-Bsymbolic-functions -lglog\
        -shared

all: nicotb_config.pb.o nicotb_vpi.o nicotb_python.o
	g++ $^ $(LDFLAGS) -o nicotb.so

nicotb_config.pb.o: nicotb_config.pb.cc
	g++ $(CFLAGS) $<

nicotb_python.o: nicotb_python.cpp nicotb_python.h
	g++ $(CFLAGS)\
		-I/usr/local/lib/python3.6/site-packages/numpy/core/include/ $<

nicotb_vpi.o: nicotb_vpi.cpp nicotb_python.h
	g++ $(CFLAGS) $<

nicotb_config.pb.cc: nicotb_config.proto
	protoc --cpp_out=. $<

clean:
	rm *.o *.so nicotb_config.pb.cc nicotb_config.pb.h
