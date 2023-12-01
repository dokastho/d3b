SRCDIR   = src
BINDIR   = bin

# list of sources used in project
SOURCES  := $(wildcard $(SRCDIR)/*.cpp)
# list of objects used in project
OBJECTS  := $(SOURCES:$(SRCDIR)/%.cpp=$(OBJDIR)/%.o)

SO_PATH = $(LD_LIBRARY_PATH)

EXE = paxos_server
RPC_LIB = drpc.so
PAXOS_LIB = paxos.so

#Default Flags
CXXFLAGS = -std=c++14 -Wconversion -Wall -Werror -Wextra -pedantic -pthread

# highest target; sews together all objects into executable
all: headers $(EXE) $(TESTS)

fast: CXXFLAGS += -ofast
fast: clean all

# make debug - will compile "all" with $(CXXFLAGS) and the -g flag
#              also defines DEBUG so that "#ifdef DEBUG /*...*/ #endif" works
debug: CXXFLAGS += -g3 -DDEBUG
debug: clean all

$(EXE): $(SRCDIR)/$(EXE).cpp $(SO_PATH)/$(PAXOS_LIB) $(SO_PATH)/$(RPC_LIB)
	@mkdir -p $(BINDIR)
	$(CXX) $(CXXFLAGS) -o $(BINDIR)/$@ $^

clean:
	rm -rf ${OBJDIR} ${BINDIR}

headers:
	cp ../../../CPPaxos/$(SRCDIR)/drpc.h ./$(SRCDIR)
	cp ../../../CPPaxos/$(SRCDIR)/Logger.h ./$(SRCDIR)
	cp ../../../CPPaxos/$(SRCDIR)/paxos.h ./$(SRCDIR)
	cp ../../../CPPaxos/$(SRCDIR)/rpcs.h ./$(SRCDIR)
	cp ../../../CPPaxos/$(SRCDIR)/Channel.h ./$(SRCDIR)
