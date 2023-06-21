#include <iostream>
#include <string>
#include <thread>
#include <vector>
#include <mutex>
#include <chrono>

#include "drpc.h"
#include "paxos.h"

#define PAXOS_START_PORT 8124
#define PAXOS_CTRL_PORT 5854
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
            ss << "paxos-" << i + 1 << "-log.log";
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
    std::mutex restart_lock;

public:
    PaxosGroup *servers;
    runner()
    {
        drpc_host my_host{"localhost", (short)PAXOS_CTRL_PORT}; 
        drpc_engine = new drpc_server(my_host, this);
        servers = new PaxosGroup(NPAXOS);
        drpc_engine->publish_endpoint("restart", (void*)runner::run);
        drpc_engine->start();
    }
    static void run(runner* rn, drpc_msg &m)
    {
        rn->restart_lock.lock();
        run_rpc *p = (run_rpc *)m.req->args;
        run_rpc *r = (run_rpc *)m.rep->args;

        if (p->cmd != 0xf)
        {
            rn->restart_lock.unlock();
            return;
        }

        r->cmd = 0xf;
        // restart server
        delete rn->servers;
        rn->servers = new PaxosGroup(NPAXOS);
        rn->restart_lock.unlock();
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
