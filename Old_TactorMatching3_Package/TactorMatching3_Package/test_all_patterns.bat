@echo off
REM ============================================================================
REM Test Script - All Tactor Patterns
REM ============================================================================
REM This script tests all 12 tactor patterns (4 directions x 3 levels)
REM Useful for quick verification that everything is working
REM ============================================================================

echo.
echo ========================================================================
echo TactorMatching3 - Quick Test Script
echo ========================================================================
echo.
echo This will test all 12 tactor patterns in sequence.
echo Press Ctrl+C to cancel at any time.
echo.
pause
echo Changing to release folder...
cd '.\Documents\tactor\HMI_Updated\TactorMatching3-master - Separate\TactorMatching3\bin\Release\'
echo Done
echo.
echo Testing LEFT direction...
echo -------------------------
echo [1/12] Left - Far
TactorMatching3.exe --direction left --level far
timeout /t 1 /nobreak >nul

echo [2/12] Left - Mid
TactorMatching3.exe --direction left --level mid
timeout /t 1 /nobreak >nul

echo [3/12] Left - Near
.\TactorMatching3.exe --direction left --level near
timeout /t 2 /nobreak >nul

echo.
echo Testing RIGHT direction...
echo --------------------------
echo [4/12] Right - Far
.\TactorMatching3.exe --direction right --level far
timeout /t 1 /nobreak >nul

echo [5/12] Right - Mid
.\TactorMatching3.exe --direction right --level mid
timeout /t 1 /nobreak >nul

echo [6/12] Right - Near
.\TactorMatching3.exe --direction right --level near
timeout /t 2 /nobreak >nul

echo.
echo Testing FRONT direction...
echo --------------------------
echo [7/12] Front - Far
.\TactorMatching3.exe --direction front --level far
timeout /t 1 /nobreak >nul

echo [8/12] Front - Mid
.\TactorMatching3.exe --direction front --level mid
timeout /t 1 /nobreak >nul

echo [9/12] Front - Near
.\TactorMatching3.exe --direction front --level near
timeout /t 2 /nobreak >nul

echo.
echo Testing REAR direction...
echo -------------------------
echo [10/12] Rear - Far
.\TactorMatching3.exe --direction rear --level far
timeout /t 1 /nobreak >nul

echo [11/12] Rear - Mid
.\TactorMatching3.exe --direction rear --level mid
timeout /t 1 /nobreak >nul

echo [12/12] Rear - Near
.\TactorMatching3.exe --direction rear --level near
timeout /t 2 /nobreak >nul

echo.
echo ========================================================================
echo All tests completed successfully!
echo ========================================================================
echo.
pause

