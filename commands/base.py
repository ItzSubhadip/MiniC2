class BaseCommand:

    name = ""
    description = ""
    usage = ""

    def __init__(self, framework):
        self.framework = framework

    def execute(self, args):
        raise NotImplementedError