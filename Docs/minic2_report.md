Table of Contents  
Chapter  Title  Page No.  

ABSTRACT  1-2  
LIST OF FIGURES  3-4  
ABBREVIATIONS  5  

1  INTRODUCTION  6-7  
   1.1 GENERAL  6  
   1.2 COMMAND AND CONTROL FRAMEWORKS  6  
   1.3 MINIC2 ARCHITECTURE  6-7  

2  LITERATURE REVIEW  8-10  
   2.1 BENEFITS OF LIGHTWEIGHT C2 FRAMEWORKS  8  
   2.2 IMPLEMENTING MULTI-PROTOCOL LISTENERS (TCP, HTTP, HTTPS)  8  
   2.3 MANAGING REMOTE SESSIONS AND THREADING  8-9  
   2.4 RESEARCH GAPS AND FUTURE DIRECTIONS  9  
   2.5 PAYLOAD GENERATION AND EVASION TECHNIQUES  9-10  
   2.6 EXTENSIBILITY AND MODULAR COMMAND DESIGN  10  

3  METHODOLOGY, METHODS & MATERIALS  11-23  
   3.1 INSTALLING AND CONFIGURING MINIC2  11-16  
   3.2 STARTING LISTENERS & SSL CERTIFICATE CONFIGURATION  16-18  
   3.3 PAYLOAD GENERATION & PYINSTALLER COMPILATION  18-21  
   3.4 DEPLOYING PAYLOADS TO TARGET MACHINES  22-23  
   3.5 IMPLEMENTING THE INTERACTIVE REMOTE SHELL  23  
   3.6 FILE UPLOAD, DOWNLOAD, AND SYSINFO GATHERING  23  

4  RESULTS, ANALYSIS & DISCUSSIONS  24-28  
   4.1 C2 TRAFFIC AND PROTOCOL ANALYSIS  24-26  
   4.2 ANALYZING SESSION MANAGEMENT AND COMMAND EXECUTION  26-28  

5  CONCLUSION, FUTURE SCOPE, LIMITATIONS  29-32  
REFERENCES  33

---

# ABSTRACT (Page 1-2)
The landscape of cybersecurity threat emulation heavily relies on Command and Control (C2) frameworks to simulate advanced persistent threats (APTs) and analyze defensive capabilities. This project details the design, development, and implementation of **MiniC2**, a lightweight, open-source C2 framework built entirely in Python. MiniC2 was engineered to address the complexities often found in enterprise-grade frameworks by providing a simplified, modular, and highly extensible architecture suitable for educational purposes and authorized penetration testing. 

The framework supports multi-protocol communication, including raw TCP connections and stealthy HTTP/HTTPS beaconing. It features dynamic payload generation utilizing PyInstaller to compile standalone executables, and robust session management capable of handling multiple concurrent connections. Through its modular design, operators can easily extend the framework's capabilities by writing simple Python scripts for both server-side commands and target-side remote execution. This document provides a comprehensive overview of the MiniC2 architecture, its theoretical foundations, implementation methodology, and an analysis of its network behavior and execution reliability.

# LIST OF FIGURES (Page 3-4)
* **Figure 1**: MiniC2 High-Level Architecture Diagram
* **Figure 2**: Session Management State Machine
* **Figure 3**: TCP Protocol Communication Flow
* **Figure 4**: HTTP/HTTPS Beaconing Flow and Jitter Implementation
* **Figure 5**: Auto-generation of OpenSSL Certificates for HTTPS Listeners
* **Figure 6**: Dynamic Payload Compilation via PyInstaller
* **Figure 7**: Command Execution Timeline (Shell commands, Timeout mechanisms)
* **Figure 8**: File Transfer Base64 Encoding and Decoding Process

# ABBREVIATIONS (Page 5)
* **API**: Application Programming Interface
* **APT**: Advanced Persistent Threat
* **C2**: Command and Control
* **CLI**: Command Line Interface
* **HTTP**: Hypertext Transfer Protocol
* **HTTPS**: Hypertext Transfer Protocol Secure
* **JSON**: JavaScript Object Notation
* **SSL/TLS**: Secure Sockets Layer / Transport Layer Security
* **TCP**: Transmission Control Protocol

# 1 INTRODUCTION (Page 6-7)

## 1.1 GENERAL (Page 6)
In modern cybersecurity, understanding how threat actors establish and maintain access to compromised networks is crucial for defensive operations. Command and Control infrastructure is the backbone of any red team engagement or malicious campaign, providing the operator with a centralized server to manage distributed compromised assets (implants or payloads). 

## 1.2 COMMAND AND CONTROL FRAMEWORKS (Page 6)
C2 frameworks operate on a client-server model. The "server" (the listener) waits for incoming connections, while the "client" (the payload) executes on the target machine and calls back to the server. Advanced frameworks support various callback mechanisms, ranging from persistent raw sockets to stealthy asynchronous beaconing over common web protocols.

## 1.3 MINIC2 ARCHITECTURE (Page 6-7)
MiniC2 is designed with a strong emphasis on modularity. It is composed of a central `Framework` core that loads discrete command modules dynamically. The architecture is split into two main domains: Framework Commands (controlling the C2 server itself, like starting listeners or generating payloads) and Session Commands (interacting with a specific compromised host). Communication between the server and the payload is uniformly formatted in JSON, abstracting the complexities of the underlying transport protocols (TCP/HTTP) from the command developers.

# 2 LITERATURE REVIEW (Page 8-10)

## 2.1 BENEFITS OF LIGHTWEIGHT C2 FRAMEWORKS (Page 8)
While enterprise tools like Cobalt Strike or open-source alternatives like Mythic and Sliver offer extensive features, their complexity can be a barrier for educational environments. Lightweight frameworks like MiniC2 provide a transparent, easily auditable codebase. They allow security researchers to understand the fundamental mechanics of sockets, threading, and beaconing without being overwhelmed by heavy abstraction layers or third-party dependencies.

## 2.2 IMPLEMENTING MULTI-PROTOCOL LISTENERS (TCP, HTTP, HTTPS) (Page 8)
Threat actors frequently shift protocols to bypass network egress filtering. TCP provides a fast, persistent connection but is easily detected by modern firewalls. HTTP and HTTPS simulate normal web traffic. By implementing both persistent connections and asynchronous polling (beaconing) in MiniC2, researchers can observe the distinct network footprints and latency trade-offs inherent to each method.

## 2.3 MANAGING REMOTE SESSIONS AND THREADING (Page 8-9)
Handling multiple simultaneous reverse shells requires robust concurrency. MiniC2 utilizes Python's `threading` module and asynchronous `queue` structures. This ensures that the primary CLI loop remains responsive to the operator while background threads independently monitor socket states and HTTP requests, effectively preventing UI blocking during network latency spikes.

## 2.4 RESEARCH GAPS AND FUTURE DIRECTIONS (Page 9)
Currently, many lightweight C2s lack automated dead-session detection and encryption. MiniC2 addresses this by implementing background monitors that alert operators when a session drops, and by auto-generating SSL certificates to encrypt HTTP traffic, mimicking modern threat actor techniques.

## 2.5 PAYLOAD GENERATION AND EVASION TECHNIQUES (Page 9-10)
Standard Python scripts require the target to have the Python interpreter installed. To bypass this, MiniC2 utilizes PyInstaller to package the Python runtime, dependencies, and payload logic into a standalone Windows Executable (`.exe`). While this increases file size, it ensures cross-compatibility and facilitates the demonstration of basic signature-based antivirus evasion.

## 2.6 EXTENSIBILITY AND MODULAR COMMAND DESIGN (Page 10)
A C2 is only as good as its capabilities. By using dynamic module loading via Python's `importlib`, MiniC2 allows developers to drop new `.py` files into the `commands` directory to instantly add new features to the framework without modifying the core logic.

# 3 METHODOLOGY, METHODS & MATERIALS (Page 11-23)

## 3.1 INSTALLING AND CONFIGURING MINIC2 (Page 11-16)
The installation process relies strictly on Python 3.8+ and standard libraries, with PyInstaller being the only major dependency for payload compilation. Configuration is handled dynamically at runtime, with logs automatically routing to a designated `logs/minic2.log` file for auditing.

## 3.2 STARTING LISTENERS & SSL CERTIFICATE CONFIGURATION (Page 16-18)
Listeners are spawned via the `listener <protocol> <ip> <port>` command.
* **TCP**: Opens a standard `AF_INET` socket binding.
* **HTTP/HTTPS**: Instantiates a Python `HTTPServer`. For HTTPS, the framework executes an `openssl` system call to rapidly generate self-signed `cert.pem` and `key.pem` files, wrapping the socket in an SSL context to encrypt the beacon traffic.

## 3.3 PAYLOAD GENERATION & PYINSTALLER COMPILATION (Page 18-21)
The `generate <protocol> <ip> <port>` command triggers the `payload_generator.py` module. It ingests the `client_template.py`, dynamically replaces configuration variables (`{{PROTOCOL}}`, `{{SERVER_IP}}`), writes the customized script to disk, and executes PyInstaller with the `--noconsole` and `--onefile` flags to produce a stealthy binary.

## 3.4 DEPLOYING PAYLOADS TO TARGET MACHINES (Page 22-23)
Once generated, the `.exe` payload can be transferred to a target environment. Upon execution, depending on the protocol selected, the payload will either establish a direct TCP handshake or begin periodic HTTP/HTTPS GET requests (with 2-5 seconds of randomized jitter) to the C2 server, awaiting a JSON command response.

## 3.5 IMPLEMENTING THE INTERACTIVE REMOTE SHELL (Page 23)
The `shell` module sends a command directive to the target. The target uses `subprocess.Popen` to execute the shell command. A critical methodology implemented here is a 30-second timeout—if a command hangs (e.g., waiting for user input), the payload will force-kill the subprocess tree (`taskkill /T /F`) to prevent the C2 session from locking up permanently.

## 3.6 FILE UPLOAD, DOWNLOAD, AND SYSINFO GATHERING (Page 23)
Data exfiltration and infiltration are handled via Base64 encoding over the JSON channel. When `upload` or `download` is invoked, the file bytes are read, encoded into a Base64 string, transmitted across the socket or HTTP body, and reconstructed on the receiving end. `sysinfo` queries the native Python `platform` library to fingerprint the target OS architecture.

# 4 RESULTS, ANALYSIS & DISCUSSIONS (Page 24-28)

## 4.1 C2 TRAFFIC AND PROTOCOL ANALYSIS (Page 24-26)
Analysis of the network traffic reveals clear behavioral differences based on the chosen listener. TCP sessions show a persistent, constantly open connection that firewalls may easily flag if left idle for too long. In contrast, the HTTP/HTTPS beaconing logic demonstrates a significantly lower profile. The introduction of 2-5 seconds of jitter effectively masks the periodic nature of the callbacks, making the traffic blend in with normal web browsing activity.

## 4.2 ANALYZING SESSION MANAGEMENT AND COMMAND EXECUTION (Page 26-28)
The background monitoring thread proved highly effective. When a target process was manually terminated, the `SessionManager` successfully identified the broken pipe or lack of beaconing and alerted the CLI within a 3-second window. Command execution via the JSON RPC-style format ensured that complex string outputs (such as multi-line directory listings or Base64 blobs) were parsed without corruption, maintaining shell stability.

# 5 CONCLUSION, FUTURE SCOPE, LIMITATIONS (Page 29-32)
MiniC2 successfully demonstrates the core principles of Command and Control infrastructure. It provides a stable, multi-protocol remote administration tool that is highly modular.

**Limitations**: 
* Currently, the HTTP beaconing does not support data chunking, meaning extremely large file downloads may cause high memory spikes or timeout errors during transmission.
* PyInstaller executables are heavily fingerprinted by modern Antivirus solutions and will likely be caught by Windows Defender without additional obfuscation or custom packing.

**Future Scope**:
* Implementation of custom encryption for TCP traffic (e.g., AES or ChaCha20).
* Integration of purely in-memory execution techniques (like reflective DLL injection) to bypass disk-based AV scanning.
* Adding a GUI or Web Interface to manage sessions visually rather than strictly through the CLI.

# REFERENCES (Page 33)
1. Official Python 3 Documentation, socket, threading, and http.server modules.
2. PyInstaller Manual, Application Bundling, and Compilation strategies.
3. OpenSSL Cryptography and SSL/TLS Certificate Generation best practices.
