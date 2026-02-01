import subprocess
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
exe_path = os.path.join(script_dir, "TactorMatching3.exe")

# Run the executable with arguments
subprocess.run([exe_path, "--direction", "left", "--level", "near"])