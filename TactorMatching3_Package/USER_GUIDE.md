# TactorMatching3 - User Guide

## Overview
This application controls haptic tactors (vibration motors) for providing tactile feedback. It can be used in two ways:
1. **UI Mode**: Interactive graphical interface for testing and development
2. **Command-Line Mode**: Automated control from Python scripts or command prompt

---

## Quick Start

### Running the UI
Simply double-click `TactorMatching3.exe` or run:
```
TactorMatching3.exe
```

### Running from Command Line
```
TactorMatching3.exe --direction seatback-left
```

---

## Default Settings

When you run a command, these are the **default values** used if you don't specify them:

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `--direction` | **REQUIRED** | Must specify: `seatback-left`, `seatback-right`, `wrist-left`, or `wrist-right` |
| `--level` | `far` | Urgency level: `far`, `mid`, or `near` |
| `--mode` | `simultaneous` | Pattern mode: `simultaneous` (all tactors at once) or `sequential` (one after another) |
| `--frequency` | `250` | Frequency in Hz (e.g., 200, 250, 300) |
| Timing | `107.5ms ON/OFF` | Custom timing (107.5ms ON, 107.5ms OFF) unless `--urgency-timing` is used |
| `--duration` | `0` | Continuous buzz duration in milliseconds (0 = single pattern) |

---

## How to Change Defaults

### Changing Urgency Level
**Default:** `far`

To change to `mid`:
```
TactorMatching3.exe --direction seatback-left --level mid
```

To change to `near`:
```
TactorMatching3.exe --direction seatback-left --level near
```

### Changing Mode (Sequential vs Simultaneous)
**Default:** `simultaneous`

To use sequential mode (tactors buzz one after another):
```
TactorMatching3.exe --direction seatback-left --mode sequential
```

To use simultaneous mode (all tactors buzz at once):
```
TactorMatching3.exe --direction seatback-left --mode simultaneous
```

### Changing Frequency
**Default:** `250` Hz

To change to 200Hz:
```
TactorMatching3.exe --direction seatback-left --frequency 200
```

To change to 300Hz:
```
TactorMatching3.exe --direction seatback-left --frequency 300
```

### Changing Timing
**Default:** Custom timing (107.5ms ON/OFF)

To use custom timing (default, no flag needed):
```
TactorMatching3.exe --direction seatback-left
```

To use urgency-based timing (timing depends on level: far/mid/near):
```
TactorMatching3.exe --direction seatback-left --urgency-timing
```

### Continuous Buzz
**Default:** Single pattern (duration = 0)

To buzz continuously for 5 seconds:
```
TactorMatching3.exe --direction seatback-left --duration 5000
```

To buzz continuously for 10 seconds:
```
TactorMatching3.exe --direction seatback-left --duration 10000
```

---

## Command Reference

### Basic Syntax
```
TactorMatching3.exe --direction <direction> [options]
```

### Required Parameter
- `--direction`: Must be one of:
  - `seatback-left` - Buzzes A1, B1, C1 tactors
  - `seatback-right` - Buzzes A2, B2, C2 tactors
  - `wrist-left` - Buzzes D1, E1, F1 tactors
  - `wrist-right` - Buzzes D2, E2, F2 tactors

### Optional Parameters
- `--level <level>`: Urgency level
  - Values: `far` (default), `mid`, `near`
  
- `--mode <mode>`: Pattern execution mode
  - Values: `simultaneous` (default), `sequential`
  - `simultaneous`: All tactors buzz at the same time
  - `sequential`: Tactors buzz one after another (A1→B1→C1)

- `--frequency <hz>`: Frequency in Hz
  - Default: `250`
  - Example: `200`, `250`, `300`

- `--urgency-timing`: Use urgency-based timing instead of custom timing
  - If not specified, uses custom timing (107.5ms ON/OFF)
  - If specified, timing depends on level (far/mid/near)

- `--duration <ms>`: Continuous buzz duration in milliseconds
  - Default: `0` (single pattern)
  - Example: `5000` (5 seconds), `10000` (10 seconds)

---

## Examples

### Example 1: Basic Command (All Defaults)
```
TactorMatching3.exe --direction seatback-left
```
This uses:
- Direction: seatback-left
- Level: far (default)
- Mode: simultaneous (default)
- Frequency: 250Hz (default)
- Timing: 107.5ms ON/OFF (default)
- Duration: 0 (single pattern, default)

### Example 2: Sequential Mode with Near Urgency
```
TactorMatching3.exe --direction wrist-right --mode sequential --level near
```

### Example 3: Custom Frequency and Continuous Buzz
```
TactorMatching3.exe --direction seatback-left --frequency 200 --duration 5000
```

### Example 4: All Parameters
```
TactorMatching3.exe --direction wrist-left --mode sequential --level mid --frequency 300 --urgency-timing --duration 3000
```

---

## Using from Python

### Basic Example
```python
import subprocess

# Simple command with defaults
subprocess.run(["TactorMatching3.exe", "--direction", "seatback-left"])
```

### With Parameters
```python
import subprocess

# Command with custom parameters
subprocess.run([
    "TactorMatching3.exe",
    "--direction", "wrist-right",
    "--mode", "sequential",
    "--level", "near",
    "--frequency", "250",
    "--duration", "5000"
])
```

### Copy Commands from Test File
Open `test_tactor_commands.py` and copy any command from the if/else blocks. Each command is explicitly written and ready to use.

---

## UI Mode

### Keyboard Controls

**Direction Keys:**
- **Q**: Seatback Left (Simultaneous)
- **W**: Seatback Right (Simultaneous)
- **O**: Seatback Left (Sequential)
- **P**: Seatback Right (Sequential)
- **A**: Wrist Left (Simultaneous)
- **S**: Wrist Right (Simultaneous)
- **K**: Wrist Left (Sequential)
- **L**: Wrist Right (Sequential)

**Urgency Level:**
- Press the direction key **1 time** = Far
- Press the direction key **2 times** = Mid
- Press the direction key **3 times** = Near

**Continuous Buzz:**
- Hold **Shift** + Direction key for continuous buzz

**Other Controls:**
- **Space**: Pause/Resume
- **ESC**: Stop
- **Numpad '+'**: Record reaction time

---

## Tactor Layout

### Seatback Tactors
- **A1, A2** (Top row)
- **B1, B2** (Middle row)
- **C1, C2** (Bottom row)

### Wrist Tactors
- **D1, D2** (Top row)
- **E1, E2** (Middle row)
- **F1, F2** (Bottom row)

### Patterns
- **seatback-left**: A1 → B1 → C1 (sequential) or A1+B1+C1 (simultaneous)
- **seatback-right**: A2 → B2 → C2 (sequential) or A2+B2+C2 (simultaneous)
- **wrist-left**: D1 → E1 → F1 (sequential) or D1+E1+F1 (simultaneous)
- **wrist-right**: D2 → E2 → F2 (sequential) or D2+E2+F2 (simultaneous)

---

## Troubleshooting

### Issue: Command doesn't work
- Make sure `TactorMatching3.exe` is in the same folder as all DLL files
- Check that you're using the correct direction name (case-sensitive)
- Verify all required DLLs are present

### Issue: Tactors don't buzz
- Check hardware connection
- Verify tactors are powered on
- Try running the UI mode to test hardware connection

### Issue: Process stays running
- The process should exit automatically after command execution
- If it doesn't, check Task Manager and end the process manually
- Make sure you're using the latest version of the executable

---

## Package Contents

This package includes:
- `TactorMatching3.exe` - Main executable
- `test_tactor_commands.py` - Python test file with all commands
- All required DLL files for standalone operation
- This user guide

---

## Support

For issues or questions, refer to the test file (`test_tactor_commands.py`) for working command examples, or use the UI mode to test your hardware setup.

