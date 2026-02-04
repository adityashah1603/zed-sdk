"""
TactorMatching3 - Python Demo Script
=====================================

This script demonstrates how to trigger tactile feedback patterns from Python
by calling the TactorMatching3.exe with command-line arguments.

SETUP REQUIREMENTS:
------------------
1. Ensure TactorMatching3.exe is in the same folder as this script
   OR update the TACTOR_EXE_PATH variable below
2. Ensure all required DLLs are in the same folder as TactorMatching3.exe:
   - TactorInterface.dll
   - eai_common.dll
   - eai_serial.dll
   - eai_winbluetooth.dll
   - eai_winusb.dll
   - Newtonsoft.Json.dll
   - mpusbapi.dll
   - SiUSBXp.dll
3. Ensure haptics.config.json is in the same folder as TactorMatching3.exe

USAGE:
------
Run this script directly: python tactor_demo.py
Or import functions for your own use: from tactor_demo import trigger_tactor

PARAMETERS:
-----------
Direction: seatback-left, seatback-right, wrist-left, wrist-right
Level: far, mid, near (optional, default: far)
Mode: sequential, simultaneous (optional, default: sequential)
Duration: optional, milliseconds to play pattern continuously
"""

import subprocess
import sys
import os
import time
from pathlib import Path


# ============================================================================
# CONFIGURATION
# ============================================================================

# Path to TactorMatching3.exe
# Option 1: Same folder as this script
TACTOR_EXE_PATH = Path(__file__).parent / "TactorMatching3.exe"

# Option 2: Relative path from current directory
# TACTOR_EXE_PATH = Path("./TactorMatching3.exe")

# Option 3: Absolute path
# TACTOR_EXE_PATH = Path(r"C:\Path\To\TactorMatching3.exe")


# ============================================================================
# CORE FUNCTION
# ============================================================================

def trigger_tactor(direction, level=None, mode=None, frequency=None, urgency_timing=False, duration_ms=None, verbose=True):
    """
    Trigger a tactor pattern.
    
    Args:
        direction (str): Direction of tactile feedback (REQUIRED)
                        Values: 'seatback-left', 'seatback-right', 'wrist-left', 'wrist-right'
        level (str, optional): Urgency level (default: 'far')
                              Values: 'far', 'mid', 'near'
        mode (str, optional): Pattern mode (default: 'sequential')
                             Values: 'sequential', 'simultaneous'
        frequency (int, optional): Frequency in Hz (default: 250)
        urgency_timing (bool, optional): Use urgency timing instead of 107.5ms (default: False)
        duration_ms (int, optional): Duration in milliseconds for continuous play
                                     If None, plays pattern once
        verbose (bool): Print execution details
    
    Returns:
        bool: True if successful, False if error
    
    Example:
        trigger_tactor('seatback-left')
        trigger_tactor('wrist-right', level='near', mode='simultaneous')
        trigger_tactor('seatback-left', level='mid', duration_ms=5000)
    """
    # Validate inputs
    valid_directions = ['seatback-left', 'seatback-right', 'wrist-left', 'wrist-right']
    valid_levels = ['far', 'mid', 'near']
    valid_modes = ['sequential', 'simultaneous']
    
    if direction.lower() not in valid_directions:
        print(f"❌ ERROR: Invalid direction '{direction}'. Must be one of: {valid_directions}")
        return False
    
    if level and level.lower() not in valid_levels:
        print(f"❌ ERROR: Invalid level '{level}'. Must be one of: {valid_levels}")
        return False
    
    if mode and mode.lower() not in valid_modes:
        print(f"❌ ERROR: Invalid mode '{mode}'. Must be one of: {valid_modes}")
        return False
    
    # Check if executable exists
    if not TACTOR_EXE_PATH.exists():
        print(f"❌ ERROR: TactorMatching3.exe not found at: {TACTOR_EXE_PATH}")
        print("   Please update TACTOR_EXE_PATH in this script or place the exe in the same folder")
        return False
    
    # Build command
    cmd = [
        str(TACTOR_EXE_PATH),
        '--direction', direction.lower()
    ]
    
    if level:
        cmd.extend(['--level', level.lower()])
    
    if mode:
        cmd.extend(['--mode', mode.lower()])
    
    if frequency:
        cmd.extend(['--frequency', str(frequency)])
    
    if urgency_timing:
        cmd.append('--urgency-timing')
    
    if duration_ms is not None:
        cmd.extend(['--duration', str(duration_ms)])
    
    # Print what we're doing
    if verbose:
        desc = f"Triggering: {direction}"
        if level:
            desc += f", level={level}"
        if mode:
            desc += f", mode={mode}"
        if frequency:
            desc += f", frequency={frequency}Hz"
        if urgency_timing:
            desc += ", urgency-timing"
        if duration_ms:
            desc += f", duration={duration_ms}ms"
        print(f"▶️  {desc}")
        print(f"   Command: {' '.join(cmd)}")
    
    try:
        # Execute the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Print output if verbose
        if verbose and result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"   {line}")
        
        # Check result
        if result.returncode == 0:
            if verbose:
                print(f"✅ Success!\n")
            return True
        else:
            print(f"❌ Failed with exit code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ ERROR: Command timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


# ============================================================================
# DEMO SCENARIOS
# ============================================================================

def demo_all_combinations():
    """
    Demonstrate all possible combinations of directions and levels.
    This is a comprehensive test of all 12 combinations (4 directions × 3 levels).
    """
    print("=" * 70)
    print("DEMO: All Direction × Level Combinations")
    print("=" * 70)
    print()
    
    directions = ['seatback-left', 'seatback-right', 'wrist-left', 'wrist-right']
    levels = ['far', 'mid', 'near']
    
    for direction in directions:
        for level in levels:
            trigger_tactor(direction, level)
            time.sleep(1)  # 1 second pause between patterns
    
    print("Demo complete!")


def demo_mode_comparison():
    """
    Demonstrate sequential vs simultaneous modes.
    """
    print("=" * 70)
    print("DEMO: Sequential vs Simultaneous Mode")
    print("=" * 70)
    print()
    
    print("Sequential mode (one by one):")
    trigger_tactor('seatback-left', mode='sequential')
    time.sleep(2)
    
    print("Simultaneous mode (all at once):")
    trigger_tactor('seatback-left', mode='simultaneous')
    time.sleep(2)
    
    print("Demo complete!")


def demo_collision_scenarios():
    """
    Demonstrate realistic collision warning scenarios.
    """
    print("=" * 70)
    print("DEMO: Realistic Collision Warning Scenarios")
    print("=" * 70)
    print()
    
    scenarios = [
        {
            'name': 'Vehicle approaching from seatback left (distant)',
            'direction': 'seatback-left',
            'level': 'far',
            'description': 'Vehicle is far but approaching from the left side'
        },
        {
            'name': 'Vehicle approaching from seatback left (close - URGENT)',
            'direction': 'seatback-left',
            'level': 'near',
            'description': 'Vehicle is very close on the left side - immediate action needed!'
        },
        {
            'name': 'Vehicle in blind spot (wrist right)',
            'direction': 'wrist-right',
            'level': 'near',
            'description': 'Vehicle in right blind spot - do not change lanes'
        },
        {
            'name': 'Wrist left warning (medium distance)',
            'direction': 'wrist-left',
            'level': 'mid',
            'description': 'Object detected on left wrist at medium distance'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['name']} ---")
        print(f"Description: {scenario['description']}")
        trigger_tactor(scenario['direction'], scenario['level'])
        time.sleep(2)  # 2 second pause between scenarios
    
    print("\nDemo complete!")


def demo_urgency_levels():
    """
    Demonstrate the three urgency levels for each direction.
    """
    print("=" * 70)
    print("DEMO: Urgency Levels (Far → Mid → Near)")
    print("=" * 70)
    print()
    
    directions = ['seatback-left', 'seatback-right', 'wrist-left', 'wrist-right']
    levels = ['far', 'mid', 'near']
    
    for direction in directions:
        print(f"\n🎯 Testing {direction.upper()} direction:")
        print("   Notice how the pattern changes with urgency...")
        
        for level in levels:
            print(f"\n   Level: {level.upper()}")
            trigger_tactor(direction, level, verbose=False)
            time.sleep(1.5)
        
        time.sleep(1)
    
    print("\nDemo complete!")


def demo_continuous_play():
    """
    Demonstrate continuous play mode with duration parameter.
    """
    print("=" * 70)
    print("DEMO: Continuous Play Mode")
    print("=" * 70)
    print()
    
    print("Playing SEATBACK-LEFT pattern continuously for 5 seconds...")
    trigger_tactor('seatback-left', duration_ms=5000)
    
    print("\nPlaying WRIST-RIGHT pattern continuously for 3 seconds...")
    trigger_tactor('wrist-right', mode='simultaneous', duration_ms=3000)
    
    print("\nDemo complete!")


# ============================================================================
# SCENARIO-BASED EXAMPLES
# ============================================================================

def scenario_lane_change_warning():
    """
    Scenario: Driver is attempting to change lanes, but there's a vehicle in blind spot.
    """
    print("=" * 70)
    print("SCENARIO: Lane Change Warning")
    print("=" * 70)
    print("\nSituation: Driver signals right turn, but vehicle detected in blind spot")
    print()
    
    # Warning sequence
    trigger_tactor('wrist-right', level='mid')
    time.sleep(0.5)
    trigger_tactor('wrist-right', level='near')
    time.sleep(0.5)
    trigger_tactor('wrist-right', level='near')
    
    print("✅ Warning delivered: Do not change lanes!")


def scenario_progressive_warning():
    """
    Scenario: Progressive warning as obstacle approaches.
    """
    print("=" * 70)
    print("SCENARIO: Progressive Warning Sequence")
    print("=" * 70)
    print("\nSituation: Obstacle detected, distance decreasing")
    print()
    
    print("Stage 1: Obstacle detected (far)...")
    trigger_tactor('seatback-left', level='far')
    time.sleep(2)
    
    print("Stage 2: Distance decreasing (mid)...")
    trigger_tactor('seatback-left', level='mid')
    time.sleep(1.5)
    
    print("Stage 3: Collision imminent - ACTION NOW! (near)...")
    trigger_tactor('seatback-left', level='near')
    time.sleep(1)
    trigger_tactor('seatback-left', level='near')
    
    print("✅ Warning sequence complete!")


def scenario_360_degree_awareness():
    """
    Scenario: Multiple vehicles detected around the car (360° awareness).
    """
    print("=" * 70)
    print("SCENARIO: 360-Degree Awareness")
    print("=" * 70)
    print("\nSituation: Dense traffic - vehicles detected in all directions")
    print()
    
    print("Scanning environment...")
    trigger_tactor('seatback-left', level='mid')
    time.sleep(0.8)
    trigger_tactor('seatback-right', level='far')
    time.sleep(0.8)
    trigger_tactor('wrist-left', level='far')
    time.sleep(0.8)
    trigger_tactor('wrist-right', level='mid')
    
    print("\n✅ 360° scan complete - driver now aware of surroundings!")


# ============================================================================
# MAIN MENU
# ============================================================================

def show_menu():
    """Display interactive menu for running demos."""
    print("\n" + "=" * 70)
    print("TactorMatching3 - Python Demo Menu")
    print("=" * 70)
    print("\nSelect a demo to run:")
    print()
    print("  1. All Combinations (12 patterns: 4 directions × 3 levels)")
    print("  2. Mode Comparison (sequential vs simultaneous)")
    print("  3. Collision Warning Scenarios (realistic examples)")
    print("  4. Urgency Levels Demo (compare far/mid/near for each direction)")
    print("  5. Continuous Play Mode (patterns with duration)")
    print()
    print("  6. Scenario: Lane Change Warning")
    print("  7. Scenario: Progressive Warning Sequence")
    print("  8. Scenario: 360-Degree Awareness")
    print()
    print("  9. Custom - Single Pattern (manual input)")
    print("  10. Test Connection (quick test)")
    print()
    print("  0. Exit")
    print()


def run_custom_pattern():
    """Allow user to manually specify direction and level."""
    print("\n--- Custom Pattern ---")
    
    direction = input("Enter direction (seatback-left/seatback-right/wrist-left/wrist-right): ").strip().lower()
    level = input("Enter level (far/mid/near) or press Enter for default 'far': ").strip().lower()
    mode = input("Enter mode (sequential/simultaneous) or press Enter for default 'sequential': ").strip().lower()
    duration = input("Enter duration in ms (or press Enter for single play): ").strip()
    
    level = level if level else None
    mode = mode if mode else None
    duration_ms = int(duration) if duration else None
    
    print()
    trigger_tactor(direction, level, mode, duration_ms=duration_ms)


def test_connection():
    """Quick test to verify the setup is working."""
    print("\n--- Connection Test ---")
    print("Running a quick test pattern (seatback-left)...\n")
    
    if trigger_tactor('seatback-left'):
        print("✅ Connection test successful!")
        print("   Your tactor setup is working correctly.")
    else:
        print("❌ Connection test failed.")
        print("   Please check:")
        print("   1. TactorMatching3.exe path is correct")
        print("   2. All required DLLs are present")
        print("   3. haptics.config.json is configured correctly")
        print("   4. Tactor hardware is connected")


def main():
    """Main entry point with interactive menu."""
    
    # Check if exe exists
    if not TACTOR_EXE_PATH.exists():
        print("=" * 70)
        print("⚠️  SETUP REQUIRED")
        print("=" * 70)
        print(f"\nERROR: TactorMatching3.exe not found at:")
        print(f"  {TACTOR_EXE_PATH}")
        print("\nPlease do one of the following:")
        print("  1. Copy TactorMatching3.exe to the same folder as this script")
        print("  2. Update TACTOR_EXE_PATH in this script (line ~48)")
        print("\nAlso ensure all required DLLs and haptics.config.json are present.")
        print("See the SETUP REQUIREMENTS section at the top of this script.")
        sys.exit(1)
    
    while True:
        show_menu()
        choice = input("Enter your choice (0-10): ").strip()
        
        if choice == '1':
            demo_all_combinations()
        elif choice == '2':
            demo_mode_comparison()
        elif choice == '3':
            demo_collision_scenarios()
        elif choice == '4':
            demo_urgency_levels()
        elif choice == '5':
            demo_continuous_play()
        elif choice == '6':
            scenario_lane_change_warning()
        elif choice == '7':
            scenario_progressive_warning()
        elif choice == '8':
            scenario_360_degree_awareness()
        elif choice == '9':
            run_custom_pattern()
        elif choice == '10':
            test_connection()
        elif choice == '0':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please enter a number between 0-10.")
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")


# ============================================================================
# DIRECT USAGE EXAMPLES (for importing this module)
# ============================================================================

def example_usage():
    """
    Example code showing how to use this module in your own Python scripts.
    """
    # Import the trigger function
    from tactor_demo import trigger_tactor
    
    # Example 1: Simple trigger (only direction - uses all defaults)
    trigger_tactor('seatback-left')
    
    # Example 2: With level
    trigger_tactor('wrist-right', level='near')
    
    # Example 3: With mode
    trigger_tactor('seatback-left', mode='simultaneous')
    
    # Example 4: Continuous play for 5 seconds
    trigger_tactor('wrist-right', duration_ms=5000)
    
    # Example 5: Sequence of warnings
    for level in ['far', 'mid', 'near']:
        trigger_tactor('seatback-left', level=level)
        time.sleep(1)
    
    # Example 6: Conditional logic
    collision_distance = 10  # meters
    if collision_distance < 5:
        trigger_tactor('seatback-left', level='near')
    elif collision_distance < 15:
        trigger_tactor('seatback-left', level='mid')
    else:
        trigger_tactor('seatback-left', level='far')


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # If run directly, show interactive menu
    main()
