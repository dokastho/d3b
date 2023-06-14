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
    test_run_lock.acquire()
    replicaserver.restart_paxos()

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
