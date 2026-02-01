# How to Build Release Package

## Quick Steps

### 1. Build in Visual Studio

1. Open `TactorMatching3.sln` in Visual Studio
2. At the top toolbar, change from "Debug" to **"Release"**
3. Press `Ctrl+Shift+B` to build
4. Wait for "Build succeeded" message

### 2. Locate the Built Files

Navigate to:
```
TactorMatching3\bin\Release\
```

### 3. Create Deployment Folder

Create a new folder (e.g., `TactorMatching3_Package`) and copy these files from `bin\Release\`:

#### Required Files:
```
✓ TactorMatching3.exe
✓ TactorMatching3.exe.config
✓ Newtonsoft.Json.dll
```

#### Tactor DLLs (if using real hardware):
```
✓ TactorInterface.dll
✓ eai_common.dll
✓ eai_serial.dll
✓ eai_winusb.dll
✓ eai_winbluetooth.dll
✓ mpusbapi.dll
✓ SiUSBXp.dll
```

#### Configuration:
```
✓ haptics.config.json (from bin\Release or project root)
```

### 4. Copy Demo Files

Copy from project root to your deployment folder:
```
✓ tactor_demo.py
✓ DEPLOYMENT_README.txt
✓ test_all_patterns.bat (optional)
```

### 5. Test Before Distributing

In your deployment folder:

**Test 1: Direct exe**
```bash
TactorMatching3.exe --direction front --level mid
```

**Test 2: UI mode**
```bash
TactorMatching3.exe
```
(Should open the UI window)

**Test 3: Python demo**
```bash
python tactor_demo.py
```

**Test 4: Batch script**
```bash
test_all_patterns.bat
```

### 6. Package and Distribute

1. Zip the entire deployment folder
2. Name it: `TactorMatching3_CommandLine_v1.0.zip`
3. Share with your team

---

## Files Checklist

Use this checklist when packaging:

```
TactorMatching3_Package/
├── [ ] TactorMatching3.exe
├── [ ] TactorMatching3.exe.config
├── [ ] Newtonsoft.Json.dll
├── [ ] TactorInterface.dll
├── [ ] eai_common.dll
├── [ ] eai_serial.dll
├── [ ] eai_winusb.dll
├── [ ] eai_winbluetooth.dll
├── [ ] mpusbapi.dll
├── [ ] SiUSBXp.dll
├── [ ] haptics.config.json
├── [ ] tactor_demo.py
├── [ ] DEPLOYMENT_README.txt
└── [ ] test_all_patterns.bat (optional)
```

---

## Alternative: PowerShell Copy Script

If you want to automate the copying, create a PowerShell script `copy_release.ps1`:

```powershell
# Create deployment folder
$deployFolder = "TactorMatching3_Package"
New-Item -ItemType Directory -Force -Path $deployFolder

# Source folder
$sourceFolder = "TactorMatching3\bin\Release"

# Copy exe and core files
Copy-Item "$sourceFolder\TactorMatching3.exe" -Destination $deployFolder
Copy-Item "$sourceFolder\TactorMatching3.exe.config" -Destination $deployFolder
Copy-Item "$sourceFolder\Newtonsoft.Json.dll" -Destination $deployFolder

# Copy tactor DLLs
Copy-Item "$sourceFolder\TactorInterface.dll" -Destination $deployFolder -ErrorAction SilentlyContinue
Copy-Item "$sourceFolder\eai_*.dll" -Destination $deployFolder -ErrorAction SilentlyContinue
Copy-Item "$sourceFolder\mpusbapi.dll" -Destination $deployFolder -ErrorAction SilentlyContinue
Copy-Item "$sourceFolder\SiUSBXp.dll" -Destination $deployFolder -ErrorAction SilentlyContinue

# Copy config
Copy-Item "$sourceFolder\haptics.config.json" -Destination $deployFolder -ErrorAction SilentlyContinue
if (!(Test-Path "$deployFolder\haptics.config.json")) {
    Copy-Item "TactorMatching3\haptics.config.json" -Destination $deployFolder -ErrorAction SilentlyContinue
}

# Copy demo files
Copy-Item "tactor_demo.py" -Destination $deployFolder
Copy-Item "DEPLOYMENT_README.txt" -Destination $deployFolder
Copy-Item "test_all_patterns.bat" -Destination $deployFolder -ErrorAction SilentlyContinue

Write-Host "Deployment package created in $deployFolder" -ForegroundColor Green
Write-Host "Test it before distributing!" -ForegroundColor Yellow
```

Run with:
```powershell
powershell -ExecutionPolicy Bypass -File copy_release.ps1
```

---

## Verification Steps

Before distributing, verify in the deployment folder:

1. **File Count Check:**
   - Should have ~15+ files
   - All DLLs present
   - Config file present

2. **Test exe directly:**
   ```bash
   TactorMatching3.exe --direction front --level mid
   ```
   Should run without errors

3. **Test Python script:**
   ```bash
   python tactor_demo.py
   ```
   Should show interactive menu

4. **Check file sizes:**
   - TactorMatching3.exe: ~10-50 KB (small, it's WPF)
   - DLLs: Various sizes
   - If files are 0 bytes, something went wrong

---

## Common Issues

### "Build failed" in Visual Studio
- Make sure you saved all files
- Check Error List window for details
- Ensure all dependencies are restored (right-click solution → Restore NuGet Packages)

### Missing DLLs in Release folder
- They might be in Debug folder
- Copy from Debug folder if needed
- Or rebuild from scratch

### Python script doesn't find exe
- Make sure exe is in same folder as tactor_demo.py
- Or update `TACTOR_EXE_PATH` in the Python script

---

## Done!

Your release package is ready to share! 🎉

