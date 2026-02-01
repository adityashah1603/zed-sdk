# TactorMatching3 - Deployment Guide

## 📦 What You Need to Deploy

This guide explains how to package and deploy the TactorMatching3 application for command-line usage from Python.

---

## 🎯 Quick Start

### For the Team Receiving the Package

1. **Extract the deployment package** to any folder
2. **Ensure tactors are connected** to your computer
3. **Run the Python demo**: `python tactor_demo.py`

That's it! Everything else is handled automatically.

---

## 📂 Required Files

When deploying TactorMatching3 to another team, you need to package these files together:

### ✅ Core Application Files

```
TactorMatching3/
├── TactorMatching3.exe          ⭐ Main executable (REQUIRED)
├── TactorMatching3.exe.config   Configuration file
├── haptics.config.json          ⭐ Haptics configuration (REQUIRED)
└── tactor_demo.py               ⭐ Python demo script (REQUIRED)
```

### ✅ .NET Dependency

```
├── Newtonsoft.Json.dll          ⭐ JSON parser (REQUIRED)
```

### ✅ Tactor Hardware DLLs (Required if using real tactors)

```
├── TactorInterface.dll          ⭐ Main tactor API (REQUIRED for hardware)
├── eai_common.dll              ⭐ EAI library (REQUIRED)
├── eai_serial.dll              ⭐ Serial communication (REQUIRED)
├── eai_winusb.dll              ⭐ USB communication (REQUIRED)
├── eai_winbluetooth.dll        Bluetooth support (optional)
├── mpusbapi.dll                USB API support
├── SiUSBXp.dll                 Silicon Labs USB support
```

### ⚠️ Important Notes

- **All files MUST be in the same folder** as TactorMatching3.exe
- The Python script can be in the same folder or any location (it will find the exe)
- Missing DLLs will cause runtime errors

---

## 🔧 How to Build and Package

### Step 1: Build the Application

1. Open the solution in Visual Studio
2. Set build mode to **Release**:
   - Menu: Build → Configuration Manager
   - Select "Release" instead of "Debug"
3. Build the project:
   - Menu: Build → Build Solution
   - Or press `Ctrl+Shift+B`

The compiled files will be in: `TactorMatching3\bin\Release\`

### Step 2: Collect Required Files

Navigate to `TactorMatching3\bin\Release\` and collect these files:

**Essential Files:**
- ✅ TactorMatching3.exe
- ✅ TactorMatching3.exe.config
- ✅ Newtonsoft.Json.dll

**Tactor Hardware DLLs:**
- ✅ TactorInterface.dll
- ✅ eai_common.dll
- ✅ eai_serial.dll
- ✅ eai_winusb.dll
- ✅ eai_winbluetooth.dll
- ✅ mpusbapi.dll
- ✅ SiUSBXp.dll

**Configuration:**
- ✅ haptics.config.json (from project root or bin\Release)

**Python Demo:**
- ✅ tactor_demo.py (from project root)

### Step 3: Create Deployment Package

Create a folder structure like this:

```
TactorMatching3_Deployment/
├── TactorMatching3.exe
├── TactorMatching3.exe.config
├── Newtonsoft.Json.dll
├── TactorInterface.dll
├── eai_common.dll
├── eai_serial.dll
├── eai_winusb.dll
├── eai_winbluetooth.dll
├── mpusbapi.dll
├── SiUSBXp.dll
├── haptics.config.json
├── tactor_demo.py
└── README.txt (optional - usage instructions)
```

### Step 4: Zip and Distribute

1. Compress the `TactorMatching3_Deployment` folder to a ZIP file
2. Send to your team
3. They extract and run!

---

## 🔌 Configuration

### haptics.config.json

This file controls the backend mode:

```json
{
  "backend": "taction",
  "participantId": "P001"
}
```

**Backend Options:**
- `"taction"` - Use real tactor hardware (default)
- `"mock"` - Use mock backend (visual-only, no hardware)

**For Testing Without Hardware:**
Change `"backend"` to `"mock"` to test without physical tactors.

---

## 🐍 Python Usage

### Option 1: Interactive Demo (Recommended for Testing)

```bash
python tactor_demo.py
```

This launches an interactive menu with:
- All 12 combinations demo
- Realistic collision scenarios
- Urgency level comparisons
- Custom pattern input
- Connection test

### Option 2: Direct Function Calls (For Integration)

```python
from tactor_demo import trigger_tactor

# Basic usage
trigger_tactor('left', 'near')

# With duration (continuous play)
trigger_tactor('front', 'mid', duration_ms=5000)

# Sequence example
for level in ['far', 'mid', 'near']:
    trigger_tactor('front', level)
    time.sleep(1)
```

### Option 3: Command Line (Direct exe call)

```bash
# Windows Command Prompt
TactorMatching3.exe --direction left --level near

# PowerShell
.\TactorMatching3.exe --direction front --level mid

# With duration
TactorMatching3.exe --direction rear --level far --duration 5000
```

### Python subprocess Example

```python
import subprocess

# Single pattern
subprocess.run([
    "TactorMatching3.exe",
    "--direction", "left",
    "--level", "near"
])

# With duration
subprocess.run([
    "TactorMatching3.exe",
    "--direction", "front",
    "--level", "mid",
    "--duration", "5000"
])
```

---

## 📋 Command-Line Reference

### Syntax

```
TactorMatching3.exe --direction <DIR> --level <LEVEL> [--duration <MS>]
```

### Parameters

| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| `--direction` | ✅ Yes | `left`, `right`, `front`, `rear` | Direction of tactile feedback |
| `--level` | ✅ Yes | `far`, `mid`, `near` | Urgency level (intensity) |
| `--duration` | ❌ No | Integer (milliseconds) | Play continuously for specified time |

### Examples

```bash
# Play left direction with near urgency (once)
TactorMatching3.exe --direction left --level near

# Play front direction with mid urgency (once)
TactorMatching3.exe --direction front --level mid

# Play rear direction with far urgency for 5 seconds continuously
TactorMatching3.exe --direction rear --level far --duration 5000

# Show help
TactorMatching3.exe --help
```

---

## 🧪 Testing the Package

Before deploying to another team, test the package:

### Test 1: Connection Test

```bash
python tactor_demo.py
# Select option 9 (Test Connection)
```

### Test 2: Single Pattern

```bash
TactorMatching3.exe --direction front --level mid
```

### Test 3: Python Integration

```python
from tactor_demo import trigger_tactor
trigger_tactor('left', 'near')
```

### Test 4: Mock Mode (No Hardware)

1. Edit `haptics.config.json`
2. Change `"backend": "taction"` to `"backend": "mock"`
3. Run any test - should see visual feedback in console

---

## ⚠️ Troubleshooting

### Error: "TactorMatching3.exe not found"

**Solution:** 
- Ensure `TactorMatching3.exe` is in the same folder as `tactor_demo.py`
- OR update `TACTOR_EXE_PATH` in `tactor_demo.py` (line ~42)

### Error: "Could not load file or assembly 'Newtonsoft.Json'"

**Solution:** 
- Ensure `Newtonsoft.Json.dll` is in the same folder as `TactorMatching3.exe`

### Error: "TactorInterface.dll not found"

**Solution:** 
- Ensure all tactor DLLs are in the same folder as `TactorMatching3.exe`
- Check the "Required Files" section above

### Error: "No TDK/Taction devices found"

**Solution:** 
1. Verify tactor hardware is physically connected
2. Check Device Manager (Windows) for the tactor device
3. Ensure device is powered on
4. Close TAction Creator software if running
5. Try "mock" mode for testing: set `"backend": "mock"` in `haptics.config.json`

### Error: "haptics.config.json not found"

**Solution:** 
- Ensure `haptics.config.json` is in the same folder as `TactorMatching3.exe`

---

## 🎓 Usage Patterns for Integration

### Pattern 1: Real-time Collision Warning

```python
import subprocess

def warn_collision(direction, distance_meters):
    """
    Trigger collision warning based on distance.
    
    Args:
        direction: 'left', 'right', 'front', 'rear'
        distance_meters: Distance to obstacle in meters
    """
    if distance_meters < 5:
        level = 'near'  # Critical
    elif distance_meters < 15:
        level = 'mid'   # Warning
    else:
        level = 'far'   # Notice
    
    subprocess.run([
        "TactorMatching3.exe",
        "--direction", direction,
        "--level", level
    ])

# Usage
warn_collision('front', 3)  # Critical front collision
warn_collision('left', 12)   # Mid-level left warning
```

### Pattern 2: Continuous Monitoring

```python
import subprocess
import threading

def continuous_warning(direction, level, stop_event):
    """
    Play continuous warning until stopped.
    
    Args:
        direction: Direction of warning
        level: Urgency level
        stop_event: threading.Event to signal stop
    """
    while not stop_event.is_set():
        subprocess.run([
            "TactorMatching3.exe",
            "--direction", direction,
            "--level", level
        ])
        stop_event.wait(0.5)  # 500ms between repeats

# Usage
stop = threading.Event()
thread = threading.Thread(target=continuous_warning, args=('left', 'near', stop))
thread.start()

# ... do other work ...

# Stop when done
stop.set()
thread.join()
```

### Pattern 3: Sequential Warnings

```python
import subprocess
import time

def progressive_warning(direction):
    """
    Progressive warning: far → mid → near
    """
    for level in ['far', 'mid', 'near']:
        subprocess.run([
            "TactorMatching3.exe",
            "--direction", direction,
            "--level", level
        ])
        time.sleep(0.5)

# Usage
progressive_warning('front')
```

---

## 📝 Notes for Developers

### Adding New Patterns

To add new tactor patterns:

1. Modify `HeadlessRunner.cs` - `BuildFrames()` method
2. Update `MainWindow.xaml.cs` - `BuildFrames()` method (keep in sync)
3. Rebuild and redeploy

### Changing Urgency Timings

To adjust burst/ISI timings:

1. Edit `HeadlessRunner.cs` - `GetUrgency()` method
2. Rebuild and redeploy

### Backend Selection

- **Mock Backend**: Test without hardware, visual-only feedback
- **Taction Backend**: Real hardware control via TactorInterface.dll

Set in `haptics.config.json`:
```json
{
  "backend": "mock"  // or "taction"
}
```

---

## 🚀 Deployment Checklist

Use this checklist when preparing a deployment package:

- [ ] Built in **Release** mode (not Debug)
- [ ] Collected all required DLLs
- [ ] Included `haptics.config.json`
- [ ] Included `tactor_demo.py`
- [ ] All files in single folder
- [ ] Tested exe directly: `TactorMatching3.exe --direction front --level mid`
- [ ] Tested Python script: `python tactor_demo.py`
- [ ] Tested with hardware (taction backend)
- [ ] Tested without hardware (mock backend)
- [ ] Created README or usage instructions
- [ ] Zipped package for distribution

---

## 📞 Support

If the receiving team encounters issues:

1. **Check all files are present** (see "Required Files" section)
2. **Verify hardware connection** (Device Manager on Windows)
3. **Test in mock mode** (set `"backend": "mock"`)
4. **Check Python version** (Python 3.6+ recommended)
5. **Review error messages** (most errors indicate missing files)

---

## 🎉 Success Criteria

The deployment is successful when:

✅ Team can run `python tactor_demo.py`  
✅ Interactive menu appears  
✅ Test connection succeeds  
✅ Tactors activate on command  
✅ Python integration works in their code  

---

**Version:** 1.0  
**Last Updated:** 2025-11-12  
**Compatible With:** TactorMatching3 v1.0+

