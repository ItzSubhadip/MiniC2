class BaseSessionCommand:
    name = ""
    description = ""
    usage = ""

    def __init__(self, session):
        self.session = session

    def execute(self, args):
        raise NotImplementedError

