from random import randint
import json

PAXOS_BUFFER_LEN = 512

class d3b_op:
    seed: int
    seq: int
    err: int
    data: json

    def __init__(self, seq = 0, json_data = None) -> None:
        self.data = json_data
        self.seq = seq
        self.err = 0
        self.seed = randint(0, 0xffffffff)

        if len(json.dumps(json_data)) > PAXOS_BUFFER_LEN:
            raise Exception(f"Data overflowed Paxos buffer len: {PAXOS_BUFFER_LEN}")

        pass

    def __bytes__(self) -> bytes:
        bb = json.dumps(self.data).encode("ascii")
        bb += (PAXOS_BUFFER_LEN - len(bb)) * b'\x00'
        bb = self.seed.to_bytes(4, "little") + self.seq.to_bytes(4, "little") + self.err.to_bytes(4, "little") + bb
        return bb

    def serialize(self, data: bytes):
        self.seed = int.from_bytes(data[:4], "little")
        self.seq = int.from_bytes(data[4:8], "little")
        self.err = int.from_bytes(data[8:12], "little")
        data = data[12:].decode('ascii').replace('\x00', '')
        self.data = json.loads(data)
        pass

    pass
