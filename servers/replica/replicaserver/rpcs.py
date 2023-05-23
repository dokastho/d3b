from random import randint

QUERY_LEN = 128
ARG_LEN = 96
MISC_LEN = 32
MISC_ITEM_LEN = 8


class d3b_op:
    seed: int
    table: str
    query: str
    args: 'list[str]'

    def __init__(self, table: str = "", query: str = "", args=[]) -> None:
        self.table = table
        self.query = query
        self.args = args
        self.seed = randint(0, 0xffffffff)

        if len(table) > MISC_ITEM_LEN:
            raise Exception("Invalid table length")

        s = 0
        for arg in args:
            s += len(arg)
            pass
        if s > ARG_LEN:
            raise Exception("Too many args in query")
        pass

    def __bytes__(self) -> bytes:
        bb = self.seed.to_bytes(4, "little")
        # encode metadata (table + arg lengths)
        misc_len = 0
        bb += self.table.encode("ascii")
        misc_len += len(self.table)
        bb += b"\x00" * (MISC_ITEM_LEN - len(self.table))
        for arg in self.args:
            bb += len(arg).to_bytes(1, "little")
            misc_len += 1
            pass
        bb += b"\x00" * (ARG_LEN - len(misc_len))

        # data payload
        bb += self.query.encode("ascii")
        bb += b"\x00" * (QUERY_LEN - len(self.query))
        for arg in self.args:
            bb += arg.encode("ascii")

        return bb

    def serialize(self, data: bytes):
        start = 0
        stop = 4
        self.seed = int.from_bytes(data[start:stop], "little")
        start = stop
        stop += MISC_ITEM_LEN
        self.table = data[start:stop].decode("ascii")

        # args
        arg_lengths = []
        for i in range(MISC_ITEM_LEN):
            start = stop
            stop += 1
            arg_lengths.append(data[start])
            pass

        start = stop
        stop += QUERY_LEN
        self.query = data[start:stop].decode("ascii")
        for n in arg_lengths:
            start = stop
            stop += n
            self.args[i] = data[start:stop].decode("ascii")
            pass

        # remove null bytes
        self.query = self.query.replace('\x00', '')
        self.table = self.table.replace('\x00', '')
        pass

    pass
