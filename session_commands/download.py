import base64
import os
from session_commands.base import BaseSessionCommand

class SessionCommand(BaseSessionCommand):
    name = "download"
    description = "Download a file from the session"
    usage = "download <remote_file> <local_file>"

    def execute(self, args):
        if len(args) != 2:
            print(f"Usage: {self.usage}")
            return

        remote_file = args[0]
        local_file = args[1]

        self.session.send({
            "type": "download",
            "file": remote_file
        })

        result = self.session.receive()
        if result and result.get("status") == "success":
            try:
                content = base64.b64decode(result["content"])
                with open(local_file, "wb") as f:
                    f.write(content)
                print(f"[+] Successfully downloaded {remote_file} to {local_file}")
            except Exception as e:
                print(f"[-] Error writing local file: {e}")
        else:
            print(f"[-] Download failed: {result.get('error', 'Unknown error')}")

