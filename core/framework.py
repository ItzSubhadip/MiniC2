import importlib
import os
import shlex
import logging
from pathlib import Path
from core.session_manager import SessionManager

_log_dir = Path(__file__).resolve().parent.parent / "logs"
_log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(_log_dir / "minic2.log"),
    ]
)

logger = logging.getLogger("minic2")

try:
    import readline

    class _Completer:
        def __init__(self, options):
            self.options = options

        def update(self, options):
            self.options = options

        def complete(self, text, state):
            matches = [o for o in self.options if o.startswith(text)]
            return matches[state] if state < len(matches) else None

    _completer = _Completer([])
    readline.set_completer(_completer.complete)
    readline.parse_and_bind("tab: complete")
except ImportError:
    _completer = None

class Framework:

    def __init__(self):
        self.listeners = []
        self.session_manager = SessionManager()
        self.commands = {}

        self._load_commands()

        if _completer:
            _completer.update(list(self.commands.keys()) + ["help", "exit"])

    def _load_commands(self):
        commands_path = Path(__file__).resolve().parent.parent / "commands"

        for file in os.listdir(commands_path):
            if file.endswith(".py") and file not in ("__init__.py", "base.py"):
                module_name = file[:-3]
                module = importlib.import_module(f"commands.{module_name}")

                command_class = getattr(module, "Command")
                command_instance = command_class(self)

                self.commands[command_instance.name] = command_instance
                logger.info(f"Loaded command: {command_instance.name}")

    def start(self):
        print("MiniC2 Framework (Type 'help' for commands)")
        logger.info("Framework started")

        while True:
            try:
                raw = input("c2 > ").strip()
                self.handle_command(raw)
            except KeyboardInterrupt:
                print("\nExiting...")
                logger.info("Framework exiting")
                break

    def handle_command(self, raw):
        if not raw:
            return

        try:
            parts = shlex.split(raw)
        except ValueError:
            parts = raw.split()

        name = parts[0]
        args = parts[1:]

        logger.info(f"Command: {name} {args}")

        if name in self.commands:
            self.commands[name].execute(args)
        else:
            print("Unknown command. Type 'help' to see available commands.")