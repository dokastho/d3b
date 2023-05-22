from random import randint

QUERY_LEN = 128
NARGS = 16
ARG_LEN = 8


class d3b_op:
    seed: int
    query: str
    args: 'list[str]'

    def __init__(self, query: str = "", *args) -> None:
        self.query = query
        self.args = [""] * NARGS
        self.seed = randint(0, 0xffffffff)

        if len(args) > NARGS:
            raise Exception("Invalid nargs in query")
        for i in range(len(args)):
            self.args[i] = args[i]
            pass
        pass

    def __bytes__(self) -> bytes:
        bb = self.seed.to_bytes(4, "little")
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
        self.seed = int.from_bytes(data[:4], "little")
        self.query = data[4:QUERY_LEN].decode("ascii")
        for i in range(NARGS):
            start_idx = 4 + QUERY_LEN + i * ARG_LEN
            self.args[i] = data[start_idx:start_idx + ARG_LEN].decode("ascii")
            pass

        pass

    pass
