import replicaserver
from pydrpc.drpc_client import *


def apply_op(Op: replicaserver.d3b_op):
    replicaserver.seq_lock.acquire()

    # perform database operation

    replicaserver.seq_lock.release()
    pass


def get_seq_num() -> int:
    replicaserver.seq_lock.acquire()

    seq = replicaserver.seq_num

    replicaserver.seq_lock.release()
    return seq


def await_reply(dh: drpc_host, m: drpc_msg):
    """perform db updates until after request is returned"""
    c = drpc_client()
    logged = False
    while not logged:
        c.Call(dh, m)
        logged = True
        apply_op(m.rep.args)

        # continue logging if the value returned isn't the one we requested to log
        if m.rep.args.seed != m.req.args.seed:
            logged = False
            continue
