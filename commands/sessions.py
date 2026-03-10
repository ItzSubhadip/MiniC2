from commands.base import BaseCommand

class Command(BaseCommand):

    name = "sessions"
    description = "List active sessions"
    usage = "sessions"

    def execute(self, args):
        self.framework.session_manager.list_sessions()