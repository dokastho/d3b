import pytest
import os
import pathlib
from pydrpc.drpc_client import *
from threading import Lock
import replicaserver


test_run_lock = Lock()


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


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to execute asserts before and after a test is run"""
    # reset seq num
    replicaserver.seq = 0

    # restart paxos server
    test_run_lock.acquire()
    paxos_host = drpc_host()
    paxos_host.hostname = "localhost"
    paxos_host.port = 5854

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

    yield

    # remove any files that are left over
    p = pathlib.Path(os.getcwd()) / 'servers' / 'replica' / 'var'
    for f in os.listdir(p):
        if f.startswith('test-'):
            os.remove(p / f)
            pass
        pass
    test_run_lock.release()
    pass
