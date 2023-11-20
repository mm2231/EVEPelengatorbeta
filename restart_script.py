import os
import sys

def restart_script():
    python = sys.executable
    os.execl(python, python, *sys.argv)

if __name__ == "__main__":
    restart_script()