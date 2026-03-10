from commands.base import BaseCommand

class Command(BaseCommand):

    name = "kill"
    description = "Close and remove a session"
    usage = "kill <session_id>"

    def execute(self, args):
        if len(args) != 1:
            print(f"Usage: {self.usage}")
            return

        try:
            sid = int(args[0])
        except ValueError:
            print("Session ID must be an integer")
            return

        if sid not in self.framework.session_manager.sessions:
            print(f"Session {sid} not found")
            return

        self.framework.session_manager.remove_session(sid)
        print(f"[+] Session {sid} killed")
