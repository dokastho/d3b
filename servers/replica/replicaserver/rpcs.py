from random import randint

QUERY_LEN = 128
ARGS_LEN = 96
MISC_LEN = 32
MISC_ITEM_LEN = 8

MEDIA_UPLOAD = 0b10000000


class d3b_op:
    seed: int
    table: str
    query: str
    args: 'list[str]'

    def __init__(self, table: str = "", query: str = "", args=[], flags = []) -> None:
        self.table = table
        self.query = query
        self.args = args
        self.seed = randint(0, 0xffffffff)
        self.flags = 0

        if len(table) > MISC_ITEM_LEN:
            raise Exception("Invalid table length")

        s = 0
        for arg in args:
            s += len(arg)
            pass
        if s > ARGS_LEN:
            raise Exception("Too many args in query")
        
        for flag in flags:
            self.flags |= flag
        pass

    def __bytes__(self) -> bytes:
        bb = self.seed.to_bytes(4, "little")
        # encode metadata (table + arg lengths)
        misc_padding = MISC_LEN
        bb += self.table.encode("ascii")
        misc_padding -= MISC_ITEM_LEN
        bb += b"\x00" * (MISC_ITEM_LEN - len(self.table))
        # add flags
        bb += self.flags.to_bytes(1, "little")
        misc_padding -= 1
        for arg in self.args:
            bb += len(arg).to_bytes(1, "little")
            misc_padding -= 1
            pass
        bb += b"\x00" * misc_padding

        # data payload
        bb += self.query.encode("ascii")
        bb += b"\x00" * (QUERY_LEN - len(self.query))
        
        arg_padding = ARGS_LEN
        for arg in self.args:
            bb += arg.encode("ascii")
            arg_padding -= len(arg)
            pass
        bb += b"\x00" * arg_padding

        return bb

    def serialize(self, data: bytes):
        start = 0
        stop = 4
        self.seed = int.from_bytes(data[start:stop], "little")
        misc_padding = MISC_LEN
        start = stop
        stop += MISC_ITEM_LEN
        misc_padding -= MISC_ITEM_LEN
        self.table = data[start:stop].decode("ascii")
        start = stop
        stop += 1
        misc_padding -= 1
        self.flags = data[start]

        # args
        arg_lengths = []
        for i in range(MISC_ITEM_LEN):
            start = stop
            stop += 1
            misc_padding -= 1
            arg_lengths.append(data[start])
            pass
        stop += misc_padding

        start = stop
        stop += QUERY_LEN
        self.query = data[start:stop].decode("ascii")
        self.args = []
        for n in arg_lengths:
            start = stop
            stop += n
            if n > 0:
                self.args.append(data[start:stop].decode("ascii"))
            pass

        # remove null bytes
        self.query = self.query.replace('\x00', '')
        self.table = self.table.replace('\x00', '')
        pass

    pass
