class Logger:
    fp = None

    def __init__(self, filename) -> None:
        self.fn = filename
        pass

    def log(self, line):
        with open(self.fn, 'a') as fp:
            fp.write(f'{line}\n')
            pass
        pass
    pass
