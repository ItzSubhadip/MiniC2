from commands.base import BaseCommand
from core.payload_generator import generate_payload

class Command(BaseCommand):

    name = "generate"
    description = "Generate a client payload (tcp, http, https)"
    usage = "generate <protocol> <ip> <port>"

    def execute(self, args):
        if len(args) != 3:
            print(f"Usage: {self.usage}")
            return

        protocol = args[0].lower()
        if protocol not in ["tcp", "http", "https"]:
            print("Invalid protocol. Use tcp, http, or https.")
            return

        generate_payload(protocol, args[1], args[2])

