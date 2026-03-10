from commands.base import BaseCommand

class Command(BaseCommand):

    name = "help"
    description = "Display available commands or detailed help for a specific command"
    usage = "help [command]"

    def execute(self, args):
        if not args:
            print("\nAvailable Commands:\n")
            for cmd in self.framework.commands.values():
                print(f"{cmd.name:<12} - {cmd.description}")
            print("\nUse 'help <command>' for detailed usage.\n")
        else:
            cmd_name = args[0]
            if cmd_name in self.framework.commands:
                cmd = self.framework.commands[cmd_name]
                print(f"\nCommand: {cmd.name}")
                print(f"Description: {cmd.description}")
                print(f"Usage: {cmd.usage}\n")
            else:
                print("Command not found.")