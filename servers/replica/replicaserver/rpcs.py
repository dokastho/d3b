from random import randint

QUERY_LEN = 128
NARGS = 7
ARG_LEN = 16


class d3b_op:
    seed: int
    table: str
    query: str
    args: 'list[str]'

    def __init__(self, table: str = "", query: str = "", *args) -> None:
        self.table = table
        self.query = query
        self.args = [""] * NARGS
        self.seed = randint(0, 0xffffffff)

        if len(table) > ARG_LEN:
            raise Exception("Invalid table length")

        if len(args) > NARGS:
            raise Exception("Invalid nargs in query")
        for i in range(len(args)):
            if len(args[i]) > ARG_LEN:
                raise Exception("Query argument is of invalid length")
            self.args[i] = args[i]
            pass
        pass

    def __bytes__(self) -> bytes:
        bb = self.seed.to_bytes(4, "little")
        bb += self.table.encode("ascii")
        bb += b"\x00" * (ARG_LEN - len(self.table))
        bb += self.query.encode("ascii")
        bb += b"\x00" * (QUERY_LEN - len(self.query))
        if len(self.args) != NARGS:
            raise Exception("Invalid nargs in query")
        for arg in self.args:

            # ensure valid argument length
            if len(arg) > ARG_LEN:
                raise Exception("Query argument is of invalid length")

            bb += arg.encode("ascii")
            bb += b"\x00" * (ARG_LEN - len(arg))

        return bb

    def serialize(self, data: bytes):
        start = 0
        stop = 4
        self.seed = int.from_bytes(data[start:stop], "little")
        start = stop
        stop += ARG_LEN
        self.table = data[start:stop].decode("ascii")
        start = stop
        stop += QUERY_LEN
        self.query = data[start:stop].decode("ascii")
        for i in range(NARGS):
            start = stop
            stop += ARG_LEN
            self.args[i] = data[start:stop].decode("ascii")
            pass

        # remove null bytes
        self.query = self.query.replace('\x00', '')
        self.table = self.table.replace('\x00', '')
        
        args: 'list[str]' = []

        for arg in self.args:
            arg = arg.replace('\x00', '')
            if arg != '':
                args.append(arg)
                pass
            pass
        self.args = args
        pass

    pass
