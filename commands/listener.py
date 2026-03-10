import threading
from commands.base import BaseCommand
from core.listener import TCPListener, HTTPListener

class Command(BaseCommand):

    name = "listener"
    description = "Start a listener (tcp, http, https)"
    usage = "listener <protocol> <ip> <port>"

    def execute(self, args):
        if len(args) != 3:
            print(f"Usage: {self.usage}")
            return

        protocol = args[0].lower()
        ip = args[1]
        port = int(args[2])

        if protocol == "tcp":
            listener = TCPListener(ip, port, self.framework.session_manager)
        elif protocol == "http":
            listener = HTTPListener(ip, port, self.framework.session_manager, use_ssl=False)
        elif protocol == "https":
            listener = HTTPListener(ip, port, self.framework.session_manager, use_ssl=True)
        else:
            print("Invalid protocol. Use tcp, http, or https.")
            return

        thread = threading.Thread(target=listener.start, daemon=True)
        thread.start()

        self.framework.listeners.append(listener)

        print(f"[+] {protocol.upper()} Listener started on {ip}:{port}")

