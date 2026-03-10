import importlib
import os
import shlex
import logging
import threading
import time
from pathlib import Path

logger = logging.getLogger("minic2")

try:
    import readline
    _has_readline = True
except ImportError:
    _has_readline = False

class SessionManager:

    def __init__(self):
        self.sessions = {}
        self.counter = 1
        self.session_commands = {}
        self._notified_dead = set()
        self._load_session_commands()
        self._start_monitor()

    def _load_session_commands(self):
        commands_path = Path(__file__).resolve().parent.parent / "session_commands"
        if not commands_path.exists():
            return

        for file in os.listdir(commands_path):
            if file.endswith(".py") and file not in ("__init__.py", "base.py"):
                module_name = file[:-3]
                module = importlib.import_module(f"session_commands.{module_name}")

                command_class = getattr(module, "SessionCommand")
                self.session_commands[command_class.name] = command_class
                logger.info(f"Loaded session command: {command_class.name}")

    def _start_monitor(self):
        thread = threading.Thread(target=self._monitor_sessions, daemon=True)
        thread.start()

    def _monitor_sessions(self):
        """Background thread: detect dead sessions and notify the operator."""
        while True:
            time.sleep(3)
            for sid, session in list(self.sessions.items()):
                if sid in self._notified_dead:
                    continue
                if not session.alive:
                    print(f"\n[!] Session {sid} has died")
                    logger.info(f"Session {sid} detected as dead")
                    self._notified_dead.add(sid)
            self._notified_dead -= self._notified_dead - set(self.sessions.keys())

    def add_session(self, session):
        session.set_id(self.counter)
        self.sessions[self.counter] = session
        print(f"\n[+] New session {self.counter} from {session.addr}")
        logger.info(f"New session {self.counter} from {session.addr}")
        self.counter += 1

    def remove_session(self, sid):
        if sid in self.sessions:
            self.sessions[sid].close()
            del self.sessions[sid]
            self._notified_dead.discard(sid)
            logger.info(f"Session {sid} removed")

    def list_sessions(self):
        if not self.sessions:
            print("No active sessions.")
            return

        for sid, session in self.sessions.items():
            status = "alive" if session.alive else "dead"
            print(f"{sid} -> {session.addr} [{status}]")

    def interact(self, sid):
        if sid not in self.sessions:
            print("Invalid session ID")
            return

        session = self.sessions[sid]

        if not session.alive:
            print(f"[!] Warning: session {sid} appears to be dead.")

        print(f"Interacting with session {sid}")
        logger.info(f"Interacting with session {sid}")

        if _has_readline:
            old_completer = readline.get_completer()
            options = list(self.session_commands.keys()) + ["bg", "exit", "help"]

            def session_complete(text, state):
                matches = [o for o in options if o.startswith(text)]
                return matches[state] if state < len(matches) else None

            readline.set_completer(session_complete)

        try:
            while True:
                try:
                    raw = input(f"session {sid} > ").strip()
                    if not raw:
                        continue

                    try:
                        parts = shlex.split(raw)
                    except ValueError:
                        parts = raw.split()

                    cmd_name = parts[0]
                    args = parts[1:]

                    if cmd_name == "bg":
                        print("Backgrounding session")
                        logger.info(f"Session {sid} backgrounded")
                        break

                    if cmd_name == "exit":
                        session.close()
                        del self.sessions[sid]
                        print("Session closed")
                        logger.info(f"Session {sid} closed by user")
                        break

                    if cmd_name == "help":
                        print("\nAvailable Session Commands:\n")
                        print(f"bg           - Background the session")
                        print(f"exit         - Close the session")
                        for name, cmd_class in self.session_commands.items():
                            print(f"{name:<12} - {cmd_class.description}")
                        print()
                        continue

                    if cmd_name in self.session_commands:
                        cmd_instance = self.session_commands[cmd_name](session)
                        cmd_instance.execute(args)
                    else:
                        print("Unknown command. Type 'help' to see available commands.")
                except KeyboardInterrupt:
                    print("\nBackgrounding session")
                    logger.info(f"Session {sid} backgrounded (Ctrl+C)")
                    break
        finally:
            # Restore previous
            if _has_readline:
                readline.set_completer(old_completer)

