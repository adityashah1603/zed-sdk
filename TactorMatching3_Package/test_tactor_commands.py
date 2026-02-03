"""
Tactor Command Test File
========================
This file contains all possible tactor commands explicitly written out.
You can copy-paste any command directly from the if/else blocks below.

Usage:
    python test_tactor_commands.py

Or copy the command strings and use them in your own Python code.
"""

import subprocess
import sys
import os

# Path to the executable (resolved relative to this script)
EXE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TactorMatching3.exe")

def run_command(command):
    """Run a tactor command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"Command: {' '.join(command) if isinstance(command, list) else command}")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        print("-" * 60)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {command}")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Main function with all commands explicitly written"""
    
    print("=" * 60)
    print("TACTOR COMMAND TEST FILE")
    print("=" * 60)
    print("\nAll commands are explicitly written below.")
    print("Copy any command string and use it in your code.\n")
    
    # Get user choice
    print("Select a command to test:")
    print("\n--- BASIC COMMANDS (Direction Only) ---")
    print("1.  Seatback Left (defaults: simultaneous, far, 250Hz, 107.5ms)")
    print("2.  Seatback Right (defaults: simultaneous, far, 250Hz, 107.5ms)")
    print("3.  Wrist Left (defaults: simultaneous, far, 250Hz, 107.5ms)")
    print("4.  Wrist Right (defaults: simultaneous, far, 250Hz, 107.5ms)")
    print("\n--- WITH MODE (Sequential vs Simultaneous) ---")
    print("5.  Seatback Left - Sequential")
    print("6.  Seatback Left - Simultaneous")
    print("7.  Seatback Right - Sequential")
    print("8.  Seatback Right - Simultaneous")
    print("9.  Wrist Left - Sequential")
    print("10. Wrist Left - Simultaneous")
    print("11. Wrist Right - Sequential")
    print("12. Wrist Right - Simultaneous")
    print("\n--- WITH URGENCY LEVEL (far/mid/near) ---")
    print("13. Seatback Left - Far")
    print("14. Seatback Left - Mid")
    print("15. Seatback Left - Near")
    print("16. Seatback Right - Far")
    print("17. Seatback Right - Mid")
    print("18. Seatback Right - Near")
    print("19. Wrist Left - Far")
    print("20. Wrist Left - Mid")
    print("21. Wrist Left - Near")
    print("22. Wrist Right - Far")
    print("23. Wrist Right - Mid")
    print("24. Wrist Right - Near")
    print("\n--- WITH MODE AND LEVEL ---")
    print("25. Seatback Left - Sequential - Far")
    print("26. Seatback Left - Sequential - Mid")
    print("27. Seatback Left - Sequential - Near")
    print("28. Seatback Left - Simultaneous - Far")
    print("29. Seatback Left - Simultaneous - Mid")
    print("30. Seatback Left - Simultaneous - Near")
    print("31. Seatback Right - Sequential - Far")
    print("32. Seatback Right - Sequential - Mid")
    print("33. Seatback Right - Sequential - Near")
    print("34. Seatback Right - Simultaneous - Far")
    print("35. Seatback Right - Simultaneous - Mid")
    print("36. Seatback Right - Simultaneous - Near")
    print("37. Wrist Left - Sequential - Far")
    print("38. Wrist Left - Sequential - Mid")
    print("39. Wrist Left - Sequential - Near")
    print("40. Wrist Left - Simultaneous - Far")
    print("41. Wrist Left - Simultaneous - Mid")
    print("42. Wrist Left - Simultaneous - Near")
    print("43. Wrist Right - Sequential - Far")
    print("44. Wrist Right - Sequential - Mid")
    print("45. Wrist Right - Sequential - Near")
    print("46. Wrist Right - Simultaneous - Far")
    print("47. Wrist Right - Simultaneous - Mid")
    print("48. Wrist Right - Simultaneous - Near")
    print("\n--- WITH FREQUENCY ---")
    print("49. Seatback Left - 250Hz (default)")
    print("50. Seatback Left - 200Hz")
    print("51. Seatback Left - 300Hz")
    print("\n--- WITH CUSTOM TIMING ---")
    print("52. Seatback Left - Custom Timing (107.5ms ON/OFF - default)")
    print("53. Seatback Left - Urgency Timing (uses level-based timing)")
    print("\n--- CONTINUOUS BUZZ ---")
    print("54. Seatback Left - Continuous (5 seconds)")
    print("55. Seatback Right - Continuous (10 seconds)")
    print("\n--- COMPLETE EXAMPLES ---")
    print("56. Seatback Left - Sequential - Near - 250Hz - Custom Timing")
    print("57. Wrist Right - Simultaneous - Far - 200Hz - Urgency Timing - Continuous 3s")
    print("\n0.  Exit")
    
    choice = input("\nEnter choice (0-57): ").strip()
    
    # All commands explicitly written - copy from here!
    if choice == "1":
        # Command: Seatback Left (all defaults)
        cmd = [EXE_PATH, "--direction", "seatback-left"]
        run_command(cmd)
        
    elif choice == "2":
        # Command: Seatback Right (all defaults)
        cmd = [EXE_PATH, "--direction", "seatback-right"]
        run_command(cmd)
        
    elif choice == "3":
        # Command: Wrist Left (all defaults)
        cmd = [EXE_PATH, "--direction", "wrist-left"]
        run_command(cmd)
        
    elif choice == "4":
        # Command: Wrist Right (all defaults)
        cmd = [EXE_PATH, "--direction", "wrist-right"]
        run_command(cmd)
        
    elif choice == "5":
        # Command: Seatback Left - Sequential
        cmd = [EXE_PATH, "--direction", "seatback-left", "--mode", "sequential"]
        run_command(cmd)
        
    elif choice == "6":
        # Command: Seatback Left - Simultaneous
        cmd = [EXE_PATH, "--direction", "seatback-left", "--mode", "simultaneous"]
        run_command(cmd)
        
    elif choice == "7":
        # Command: Seatback Right - Sequential
        cmd = [EXE_PATH, "--direction", "seatback-right", "--mode", "sequential"]
        run_command(cmd)
        
    elif choice == "8":
        # Command: Seatback Right - Simultaneous
        cmd = [EXE_PATH, "--direction", "seatback-right", "--mode", "simultaneous"]
        run_command(cmd)
        
    elif choice == "9":
        # Command: Wrist Left - Sequential
        cmd = [EXE_PATH, "--direction", "wrist-left", "--mode", "sequential"]
        run_command(cmd)
        
    elif choice == "10":
        # Command: Wrist Left - Simultaneous
        cmd = [EXE_PATH, "--direction", "wrist-left", "--mode", "simultaneous"]
        run_command(cmd)
        
    elif choice == "11":
        # Command: Wrist Right - Sequential
        cmd = [EXE_PATH, "--direction", "wrist-right", "--mode", "sequential"]
        run_command(cmd)
        
    elif choice == "12":
        # Command: Wrist Right - Simultaneous
        cmd = [EXE_PATH, "--direction", "wrist-right", "--mode", "simultaneous"]
        run_command(cmd)
        
    elif choice == "13":
        # Command: Seatback Left - Far
        cmd = [EXE_PATH, "--direction", "seatback-left", "--level", "far"]
        run_command(cmd)
        
    elif choice == "14":
        # Command: Seatback Left - Mid
        cmd = [EXE_PATH, "--direction", "seatback-left", "--level", "mid"]
        run_command(cmd)
        
    elif choice == "15":
        # Command: Seatback Left - Near
        cmd = [EXE_PATH, "--direction", "seatback-left", "--level", "near"]
        run_command(cmd)
        
    elif choice == "16":
        # Command: Seatback Right - Far
        cmd = [EXE_PATH, "--direction", "seatback-right", "--level", "far"]
        run_command(cmd)
        
    elif choice == "17":
        # Command: Seatback Right - Mid
        cmd = [EXE_PATH, "--direction", "seatback-right", "--level", "mid"]
        run_command(cmd)
        
    elif choice == "18":
        # Command: Seatback Right - Near
        cmd = [EXE_PATH, "--direction", "seatback-right", "--level", "near"]
        run_command(cmd)
        
    elif choice == "19":
        # Command: Wrist Left - Far
        cmd = [EXE_PATH, "--direction", "wrist-left", "--level", "far"]
        run_command(cmd)
        
    elif choice == "20":
        # Command: Wrist Left - Mid
        cmd = [EXE_PATH, "--direction", "wrist-left", "--level", "mid"]
        run_command(cmd)
        
    elif choice == "21":
        # Command: Wrist Left - Near
        cmd = [EXE_PATH, "--direction", "wrist-left", "--level", "near"]
        run_command(cmd)
        
    elif choice == "22":
        # Command: Wrist Right - Far
        cmd = [EXE_PATH, "--direction", "wrist-right", "--level", "far"]
        run_command(cmd)
        
    elif choice == "23":
        # Command: Wrist Right - Mid
        cmd = [EXE_PATH, "--direction", "wrist-right", "--level", "mid"]
        run_command(cmd)
        
    elif choice == "24":
        # Command: Wrist Right - Near
        cmd = [EXE_PATH, "--direction", "wrist-right", "--level", "near"]
        run_command(cmd)
        
    elif choice == "25":
        # Command: Seatback Left - Sequential - Far
        cmd = [EXE_PATH, "--direction", "seatback-left", "--mode", "sequential", "--level", "far"]
        run_command(cmd)
        
    elif choice == "26":
        # Command: Seatback Left - Sequential - Mid
        cmd = [EXE_PATH, "--direction", "seatback-left", "--mode", "sequential", "--level", "mid"]
        run_command(cmd)
        
    elif choice == "27":
        # Command: Seatback Left - Sequential - Near
        cmd = [EXE_PATH, "--direction", "seatback-left", "--mode", "sequential", "--level", "near"]
        run_command(cmd)
        
    elif choice == "28":
        # Command: Seatback Left - Simultaneous - Far
        cmd = [EXE_PATH, "--direction", "seatback-left", "--mode", "simultaneous", "--level", "far"]
        run_command(cmd)
        
    elif choice == "29":
        # Command: Seatback Left - Simultaneous - Mid
        cmd = [EXE_PATH, "--direction", "seatback-left", "--mode", "simultaneous", "--level", "mid"]
        run_command(cmd)
        
    elif choice == "30":
        # Command: Seatback Left - Simultaneous - Near
        cmd = [EXE_PATH, "--direction", "seatback-left", "--mode", "simultaneous", "--level", "near"]
        run_command(cmd)
        
    elif choice == "31":
        # Command: Seatback Right - Sequential - Far
        cmd = [EXE_PATH, "--direction", "seatback-right", "--mode", "sequential", "--level", "far"]
        run_command(cmd)
        
    elif choice == "32":
        # Command: Seatback Right - Sequential - Mid
        cmd = [EXE_PATH, "--direction", "seatback-right", "--mode", "sequential", "--level", "mid"]
        run_command(cmd)
        
    elif choice == "33":
        # Command: Seatback Right - Sequential - Near
        cmd = [EXE_PATH, "--direction", "seatback-right", "--mode", "sequential", "--level", "near"]
        run_command(cmd)
        
    elif choice == "34":
        # Command: Seatback Right - Simultaneous - Far
        cmd = [EXE_PATH, "--direction", "seatback-right", "--mode", "simultaneous", "--level", "far"]
        run_command(cmd)
        
    elif choice == "35":
        # Command: Seatback Right - Simultaneous - Mid
        cmd = [EXE_PATH, "--direction", "seatback-right", "--mode", "simultaneous", "--level", "mid"]
        run_command(cmd)
        
    elif choice == "36":
        # Command: Seatback Right - Simultaneous - Near
        cmd = [EXE_PATH, "--direction", "seatback-right", "--mode", "simultaneous", "--level", "near"]
        run_command(cmd)
        
    elif choice == "37":
        # Command: Wrist Left - Sequential - Far
        cmd = [EXE_PATH, "--direction", "wrist-left", "--mode", "sequential", "--level", "far"]
        run_command(cmd)
        
    elif choice == "38":
        # Command: Wrist Left - Sequential - Mid
        cmd = [EXE_PATH, "--direction", "wrist-left", "--mode", "sequential", "--level", "mid"]
        run_command(cmd)
        
    elif choice == "39":
        # Command: Wrist Left - Sequential - Near
        cmd = [EXE_PATH, "--direction", "wrist-left", "--mode", "sequential", "--level", "near"]
        run_command(cmd)
        
    elif choice == "40":
        # Command: Wrist Left - Simultaneous - Far
        cmd = [EXE_PATH, "--direction", "wrist-left", "--mode", "simultaneous", "--level", "far"]
        run_command(cmd)
        
    elif choice == "41":
        # Command: Wrist Left - Simultaneous - Mid
        cmd = [EXE_PATH, "--direction", "wrist-left", "--mode", "simultaneous", "--level", "mid"]
        run_command(cmd)
        
    elif choice == "42":
        # Command: Wrist Left - Simultaneous - Near
        cmd = [EXE_PATH, "--direction", "wrist-left", "--mode", "simultaneous", "--level", "near"]
        run_command(cmd)
        
    elif choice == "43":
        # Command: Wrist Right - Sequential - Far
        cmd = [EXE_PATH, "--direction", "wrist-right", "--mode", "sequential", "--level", "far"]
        run_command(cmd)
        
    elif choice == "44":
        # Command: Wrist Right - Sequential - Mid
        cmd = [EXE_PATH, "--direction", "wrist-right", "--mode", "sequential", "--level", "mid"]
        run_command(cmd)
        
    elif choice == "45":
        # Command: Wrist Right - Sequential - Near
        cmd = [EXE_PATH, "--direction", "wrist-right", "--mode", "sequential", "--level", "near"]
        run_command(cmd)
        
    elif choice == "46":
        # Command: Wrist Right - Simultaneous - Far
        cmd = [EXE_PATH, "--direction", "wrist-right", "--mode", "simultaneous", "--level", "far"]
        run_command(cmd)
        
    elif choice == "47":
        # Command: Wrist Right - Simultaneous - Mid
        cmd = [EXE_PATH, "--direction", "wrist-right", "--mode", "simultaneous", "--level", "mid"]
        run_command(cmd)
        
    elif choice == "48":
        # Command: Wrist Right - Simultaneous - Near
        cmd = [EXE_PATH, "--direction", "wrist-right", "--mode", "simultaneous", "--level", "near"]
        run_command(cmd)
        
    elif choice == "49":
        # Command: Seatback Left - 250Hz (default)
        cmd = [EXE_PATH, "--direction", "seatback-left", "--frequency", "250"]
        run_command(cmd)
        
    elif choice == "50":
        # Command: Seatback Left - 200Hz
        cmd = [EXE_PATH, "--direction", "seatback-left", "--frequency", "200"]
        run_command(cmd)
        
    elif choice == "51":
        # Command: Seatback Left - 300Hz
        cmd = [EXE_PATH, "--direction", "seatback-left", "--frequency", "300"]
        run_command(cmd)
        
    elif choice == "52":
        # Command: Seatback Left - Custom Timing (107.5ms ON/OFF - default)
        cmd = [EXE_PATH, "--direction", "seatback-left"]
        # Note: Custom timing is default, no flag needed
        run_command(cmd)
        
    elif choice == "53":
        # Command: Seatback Left - Urgency Timing (uses level-based timing)
        cmd = [EXE_PATH, "--direction", "seatback-left", "--urgency-timing"]
        run_command(cmd)
        
    elif choice == "54":
        # Command: Seatback Left - Continuous (5 seconds)
        cmd = [EXE_PATH, "--direction", "seatback-left", "--duration", "5000"]
        run_command(cmd)
        
    elif choice == "55":
        # Command: Seatback Right - Continuous (10 seconds)
        cmd = [EXE_PATH, "--direction", "seatback-right", "--duration", "10000"]
        run_command(cmd)
        
    elif choice == "56":
        # Command: Seatback Left - Sequential - Near - 250Hz - Custom Timing
        cmd = [EXE_PATH, "--direction", "seatback-left", "--mode", "sequential", "--level", "near", "--frequency", "250"]
        run_command(cmd)
        
    elif choice == "57":
        # Command: Wrist Right - Simultaneous - Far - 200Hz - Urgency Timing - Continuous 3s
        cmd = [EXE_PATH, "--direction", "wrist-right", "--mode", "simultaneous", "--level", "far", "--frequency", "200", "--urgency-timing", "--duration", "3000"]
        run_command(cmd)
        
    elif choice == "0":
        print("Exiting...")
        sys.exit(0)
        
    else:
        print("Invalid choice. Please select 0-57.")
        return
    
    print("\nCommand executed. Check above for results.")
    print("\nTo copy a command, look at the 'cmd' variable in the corresponding if/else block above.")

if __name__ == "__main__":
    main()

