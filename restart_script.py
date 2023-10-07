import subprocess
import sys

def restart_script():
    subprocess.Popen([sys.executable, "main.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    sys.exit(0)