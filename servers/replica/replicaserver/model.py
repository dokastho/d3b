import replicaserver
from pydrpc.drpc_client import *


def apply_op(Op: replicaserver.d3b_op):
    replicaserver.seq_lock.acquire()

    # perform database operation

    # update seq number
    replicaserver.seq_num = Op.seq + 1

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

        # continue logging if the seq num has not been reached
        if m.rep.args.Op.seq != m.req.args.seq:
            apply_op(m.rep.args.Op)
            logged = False
            m.req.args.seq = get_seq_num()
            continue

        # continue logging if the value returned isn't the one we requested to log
        if m.rep.args.Op.seed != m.req.args.seed:
            apply_op(m.rep.args.Op)
            logged = False
            m.req.args.seq = get_seq_num()
            continue
