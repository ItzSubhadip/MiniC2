# MiniC2 Framework Details

This document provides a comprehensive breakdown of the internal workings of the **MiniC2** framework, detailing every Python file, its purpose, and how it contributes to the overall architecture.

## Overview

MiniC2 is a lightweight, modular Command and Control (C2) framework written entirely in Python. It is designed to demonstrate how C2 architecture functions, featuring multi-protocol listeners (TCP, HTTP, HTTPS), dynamic payload generation via PyInstaller, and interactive session management.

---

## 1. Entry Point

### `main.py`
This is the main entry point of the framework. Its sole responsibility is to instantiate the `Framework` class from `core.framework` and invoke its `start()` method.

---

## 2. Core Modules (`core/`)

The `core` directory houses the foundational components that drive the framework's logic.

### `core/framework.py`
This file implements the `Framework` class, which acts as the central brain of the CLI.
- **Initialization**: It sets up the logging system (logging to `logs/minic2.log`), initializes the `SessionManager`, and dynamically loads all available framework commands from the `commands/` directory using Python's `importlib`.
- **CLI Loop**: The `start()` method drops the user into an interactive loop (`c2 >`), utilizing `readline` to provide auto-completion for loaded commands.
- **Command Dispatcher**: The `handle_command()` method splits user input (using `shlex`) and dispatches execution to the corresponding command class.

### `core/session_manager.py`
The `SessionManager` tracks and manages all active connections (sessions) from remote targets.
- **Session Tracking**: It assigns unique IDs to incoming sessions and stores them in a dictionary.
- **Dead Session Monitor**: It spawns a background daemon thread (`_monitor_sessions`) that checks the `.alive` status of all sessions every 3 seconds, notifying the user immediately if a session dies.
- **Session Interaction**: The `interact()` method (`use <id>`) drops the user into a session-specific console. It dynamically loads commands from the `session_commands/` folder and swaps the auto-completer to provide session-specific tab-completion.

### `core/session.py`
This file defines the logical representation of an active connection.
- **`BaseSession`**: The abstract class that provides standard properties like `id` and `alive`, and outlines the `send` and `receive` interfaces.
- **`TCPSession`**: Implements raw socket communication. It spawns a dedicated daemon thread (`_recv_loop`) to continuously listen for incoming JSON data over the socket, buffering it and parsing it into a queue to prevent blocking the main CLI.
- **`HTTPSession`**: Represents an HTTP/HTTPS beacon. Because HTTP is stateless, it relies on two asynchronous queues (`command_queue` and `result_queue`). Commands are queued up until the target beacon checks in via a GET request to fetch them.

### `core/listener.py`
This file handles the server-side listening sockets for incoming target connections.
- **`TCPListener`**: Opens a standard TCP socket binding. When a target connects, it wraps the raw socket in a `TCPSession` object and passes it to the `SessionManager`.
- **`HTTPListener` & `HTTPRequestHandler`**: Implements a custom HTTP server. 
  - `do_GET()`: The target polls this endpoint. If it's a new target, an `HTTPSession` is created and an `X-Session-ID` is assigned. If there are pending commands in the session's queue, they are sent; otherwise, a `noop` is sent.
  - `do_POST()`: The target posts command execution results back here. The results are parsed and placed into the session's result queue.
  - **SSL Support**: If HTTPS is requested, it automatically utilizes OpenSSL to generate a self-signed `cert.pem` and `key.pem` and wraps the server socket in a TLS context.

### `core/payload_generator.py`
Responsible for weaponizing the payload template.
- It takes the user's requested protocol, IP, and port.
- It reads `payloads/templates/client_template.py`, replacing placeholders like `{{PROTOCOL}}` and `{{SERVER_IP}}` with the user's configuration.
- It dumps the new python file into `payloads/generated/` and invokes PyInstaller via `subprocess.run` to compile the Python script into a standalone `.exe` payload without a console window (`--noconsole`).

---

## 3. Framework Commands (`commands/`)

These modules are automatically loaded by the `Framework` class and represent the root-level commands available in the C2 console.

- **`base.py`**: Defines the `BaseCommand` class which all framework commands must inherit. Requires a `name`, `description`, `usage`, and `execute()` method.
- **`listener.py`**: Parses arguments (protocol, IP, port), instantiates the corresponding listener from `core.listener` (`TCPListener` or `HTTPListener`), and runs it in a background thread so the user can continue using the console.
- **`generate.py`**: Calls the `generate_payload` function from `core.payload_generator` to build the target executable.
- **`sessions.py`**: Iterates through the `SessionManager` and prints all active and dead sessions.
- **`use.py`**: Triggers the `SessionManager.interact()` loop to start interacting with a specific session ID.
- **`kill.py`**: Safely closes a socket/session and removes it from the manager.
- **`help.py`**: Dynamically generates help text by iterating over the loaded command modules and reading their `description` and `usage` attributes.

---

## 4. Session Commands (`session_commands/`)

These modules are dynamically loaded when interacting with a specific session. They execute actions on the target machine.

- **`base.py`**: Defines the `BaseSessionCommand`. It holds a reference to the active `session` object so commands can use `self.session.send()` and `self.session.receive()`.
- **`shell.py`**: Takes raw user input, formats it into a JSON dictionary `{"type": "shell", "command": "..."}`, sends it to the target, waits for the response, and prints the stdout/stderr.
- **`upload.py`**: Reads a local file, encodes its binary content into Base64, and sends a JSON payload containing the filename and Base64 content to the target to be written to disk.
- **`download.py`**: Sends a download request. The target replies with a Base64 encoded string of the requested file, which this module decodes and saves locally.
- **`sysinfo.py`**: Sends a request for system architecture data (OS, architecture, hostname) and formats the JSON response into a readable table.

---

## 5. Payloads (`payloads/`)

### `payloads/templates/client_template.py`
This is the raw implant code that gets executed on the target's machine.
- **Command Handler (`handle_command`)**: A centralized function that parses incoming JSON commands. It supports `shell` (executes via `subprocess.Popen` with a 30-second timeout killswitch), `upload` (decodes base64 and writes to disk), `download` (reads disk, encodes base64, and returns), `sysinfo` (uses the `platform` module), and `exit` (kills the process).
- **TCP Logic (`run_tcp`)**: Opens a raw socket to the server, reads bytes, splits them by newline `\n`, parses the JSON, executes the command, and sends the JSON result back.
- **HTTP/HTTPS Logic (`run_http`)**: Operates on a beaconing loop. It makes a `urllib` GET request every 2 to 5 seconds. If it receives a command, it executes it and sends a POST request with the results. It utilizes a custom SSL context (`ssl.CERT_NONE`) to ignore the server's self-signed certificate warnings.
