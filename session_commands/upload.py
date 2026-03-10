import base64
import os
from session_commands.base import BaseSessionCommand

class SessionCommand(BaseSessionCommand):
    name = "upload"
    description = "Upload a file to the session"
    usage = "upload <local_file> <remote_file>"

    def execute(self, args):
        if len(args) != 2:
            print(f"Usage: {self.usage}")
            return

        local_file = args[0]
        remote_file = args[1]

        if not os.path.exists(local_file):
            print(f"Local file {local_file} not found.")
            return

        try:
            with open(local_file, "rb") as f:
                content = base64.b64encode(f.read()).decode()

            self.session.send({
                "type": "upload",
                "dest": remote_file,
                "content": content
            })

            result = self.session.receive()
            if result and result.get("status") == "success":
                print(f"[+] Successfully uploaded {local_file} to {remote_file}")
            else:
                print(f"[-] Upload failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"[-] Error reading local file: {e}")

