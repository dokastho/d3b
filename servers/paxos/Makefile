SO_PATH = $(LD_LIBRARY_PATH)

EXE = paxos_server
RPC_LIB = drpc.so
PAXOS_LIB = paxos.so

#Default Flags
CXXFLAGS = -std=c++14 -Wconversion -Wall -Werror -Wextra -pedantic -pthread

# make debug - will compile "all" with $(CXXFLAGS) and the -g flag
#              also defines DEBUG so that "#ifdef DEBUG /*...*/ #endif" works
debug: CXXFLAGS += -g3 -DDEBUG
debug: clean all

# highest target; sews together all objects into executable
all: $(EXE)

$(EXE): $(EXE).cpp $(SO_PATH)/$(PAXOS_LIB) $(SO_PATH)/$(RPC_LIB)
	$(CXX) $(CXXFLAGS) -o $@ $^

clean:
	rm -f $(OBJECTS) $(EXECUTABLE) $(TESTS) $(PARTIAL_SUBMITFILE) $(FULL_SUBMITFILE) *.out paxos_server

headers:
	cp ../../../CPPaxos/drpc.h .
	cp ../../../CPPaxos/Logger.h .
	cp ../../../CPPaxos/paxos.h .
	cp ../../../CPPaxos/rpcs.h .

# rule for creating objects
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -fPIC -g -c $*.cpp
