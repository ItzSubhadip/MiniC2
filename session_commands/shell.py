from session_commands.base import BaseSessionCommand

class SessionCommand(BaseSessionCommand):
    name = "shell"
    description = "Drop into a system shell"
    usage = "shell"

    def execute(self, args):
        print("Entering system shell. Type 'exit' to return to session menu.")
        while True:
            try:
                cmd = input(f"session {self.session.id} (shell) > ").strip()
                if not cmd:
                    continue
                if cmd == "exit":
                    break

                self.session.send({"type": "shell", "command": cmd})

                result = None
                while result is None:
                    if not self.session.alive:
                        print("[-] Session died.")
                        return
                    result = self.session.receive(timeout=0.5)

                if "output" in result:
                    print(result["output"])
                else:
                    print("No response or error.")
            except KeyboardInterrupt:
                print("\nReturning to session menu...")
                break

