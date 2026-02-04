================================================================================
TactorMatching3 - Command-Line Control Package
================================================================================

QUICK START:
------------
1. Ensure all files are in the same folder
2. Connect tactor hardware to your computer
3. Run: python tactor_demo.py
4. Select a demo from the menu

USAGE FROM PYTHON:
------------------
Option 1 - Import the function:
    from tactor_demo import trigger_tactor
    trigger_tactor('left', 'near')

Option 2 - Direct command:
    subprocess.run(["TactorMatching3.exe", "--direction", "left", "--level", "near"])

COMMAND-LINE SYNTAX:
--------------------
TactorMatching3.exe --direction <DIR> --level <LEVEL> [--duration <MS>]

Parameters:
  --direction   left, right, front, rear
  --level       far, mid, near
  --duration    (optional) milliseconds for continuous play

Examples:
  TactorMatching3.exe --direction left --level near
  TactorMatching3.exe --direction front --level mid
  TactorMatching3.exe --direction rear --level far --duration 5000

REQUIRED FILES:
---------------
✓ TactorMatching3.exe (main executable)
✓ TactorMatching3.exe.config
✓ Newtonsoft.Json.dll
✓ haptics.config.json
✓ tactor_demo.py

Tactor Hardware DLLs (required if using real tactors):
✓ TactorInterface.dll
✓ TActionManager.dll
✓ eai_common.dll
✓ eai_serial.dll
✓ eai_winusb.dll
✓ eai_winbluetooth.dll
✓ mpusbapi.dll
✓ SiUSBXp.dll

TESTING WITHOUT HARDWARE:
-------------------------
Edit haptics.config.json and change:
  "backend": "taction"
to:
  "backend": "mock"

This enables visual-only mode (no hardware required).

TROUBLESHOOTING:
----------------
Error: "exe not found"
  → Ensure TactorMatching3.exe is in same folder as tactor_demo.py

Error: "DLL not found"
  → Ensure all DLLs are in same folder as TactorMatching3.exe

Error: "No devices found"
  → Check hardware connection
  → Try mock mode (see above)
  → Close TAction Creator if running

PYTHON REQUIREMENTS:
--------------------
- Python 3.6 or higher
- No additional packages required (uses only standard library)

SUPPORT:
--------
See DEPLOYMENT_GUIDE.md for detailed documentation

================================================================================

