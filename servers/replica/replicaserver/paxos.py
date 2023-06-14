import replicaserver
from pydrpc.drpc_client import *
from d3b_client.client import *


class paxos_restart_op:
    cmd: int

    def __init__(self, cmd) -> None:
        self.cmd = cmd
        pass

    def __bytes__(self) -> bytes:
        return self.cmd.to_bytes(4, "little")

    def serialize(self, data: bytes):
        self.cmd = int.from_bytes(data, "little")
        pass


def restart_paxos():
    """Fixture to execute asserts before and after a test is run"""
    # reset seq num
    replicaserver.seq = 0

    # restart paxos server
    paxos_host = drpc_host()
    paxos_host.hostname = "localhost"
    paxos_host.port = replicaserver.app.config["PAXOS_CTRL_PORT"]

    req = paxos_restart_op(15)
    rep = paxos_restart_op(0)
    mreq = drpc_arg_wrapper(req)
    mrep = drpc_arg_wrapper(rep)
    msg = drpc_msg()
    msg.req = mreq
    msg.rep = mrep
    msg.target = "restart"

    c = drpc_client()
    c.Call(paxos_host, msg)
    pass
