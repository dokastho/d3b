#include <iostream>
#include <string>
#include <thread>
#include <vector>

#include "drpc.h"
#include "paxos.h"

#define PAXOS_START_PORT 8124
#define NPAXOS 3

struct run_rpc
{
    int cmd;
};

class PaxosGroup
{
public:
    std::vector<drpc_host> hosts;
    std::vector<Paxos *> pxa;
    PaxosGroup(const int npaxos)
    {
        for (int i = 0; i < npaxos; i++)
        {
            drpc_host h{"localhost", (short)(PAXOS_START_PORT + i)};
            hosts.push_back(h);
        }
        for (int i = 0; i < npaxos; i++)
        {
            std::stringstream ss;
            ss << "output" << i << ".out";
            Paxos *p = new Paxos(i, ss.str(), hosts);
            pxa.push_back(p);
        }
    }

    ~PaxosGroup()
    {
        for (size_t i = 0; i < pxa.size(); i++)
        {
            delete pxa[i];
        }
    }
};

class runner
{
private:
    drpc_server *drpc_engine;

public:
    PaxosGroup *servers;
    runner()
    {
        drpc_host my_host{"localhost", (short)5854};
        drpc_engine = new drpc_server(my_host, this);
        servers = new PaxosGroup(NPAXOS);
        drpc_engine->publish_endpoint("restart", (void*)runner::run);
        std::thread t(&drpc_server::run_server, drpc_engine);
        t.detach();
    }
    static void run(runner* rn, drpc_msg &m)
    {
        run_rpc *p = (run_rpc *)m.req->args;
        run_rpc *r = (run_rpc *)m.rep->args;

        if (p->cmd != 0xf)
        {
            return;
        }

        r->cmd = 0xf;
        // restart server
        delete rn->servers;
        rn->servers = new PaxosGroup(NPAXOS);
        
    }
    ~runner()
    {
        delete drpc_engine;
    }

};


int main()
{
    runner R;
    std::string cmd = "";
    do
    {
        std::cout << "enter 'q' to quit\n$ ";
        std::cin >> cmd;
    } while (cmd[0] != 'q');
}
