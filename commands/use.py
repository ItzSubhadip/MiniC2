from commands.base import BaseCommand

class Command(BaseCommand):

    name = "use"
    description = "Interact with a specific session"
    usage = "use <session_id>"

    def execute(self, args):
        if len(args) != 1:
            print(f"Usage: {self.usage}")
            return

        try:
            sid = int(args[0])
            self.framework.session_manager.interact(sid)
        except ValueError:
            print("Session ID must be an integer")