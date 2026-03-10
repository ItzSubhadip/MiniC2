from session_commands.base import BaseSessionCommand

class SessionCommand(BaseSessionCommand):
    name = "sysinfo"
    description = "Get system information"
    usage = "sysinfo"

    def execute(self, args):
        self.session.send({"type": "sysinfo"})
        result = self.session.receive()
        
        if result and result.get("status") == "success":
            info = result.get("info", {})
            print("\nSystem Information:")
            print("-" * 20)
            print(f"OS:        {info.get('system', 'Unknown')} {info.get('release', '')}")
            print(f"Node:      {info.get('node', 'Unknown')}")
            print(f"Version:   {info.get('version', 'Unknown')}")
            print(f"Machine:   {info.get('machine', 'Unknown')}")
            print(f"Processor: {info.get('processor', 'Unknown')}")
            print("-" * 20 + "\n")
        else:
            print(f"[-] Failed to get sysinfo: {result.get('error', 'Unknown error') if result else 'No response'}")
