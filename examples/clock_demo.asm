# CPU Clock Speed Demo
# This program demonstrates the impact of CPU clock frequency
# Counts from 0 to 9 and displays each number

# Display numbers 0-9
# Best viewed with live display: ./run.sh -l examples/clock_demo.asm

ADDI x10, x0, 0         # Counter starts at 0
ADDI x11, x0, 10        # Max count = 10
ADDI x12, x0, 0xF0000   # Display buffer base

loop:
    # Write counter to display
    ADDI x13, x10, 48   # Convert to ASCII ('0' + counter)
    
    # Calculate display position (counter * 4 for spacing)
    ADD x14, x10, x10   # x14 = counter * 2
    ADD x14, x14, x14   # x14 = counter * 4
    ADD x15, x12, x14   # x15 = display base + offset
    
    SB x13, 0(x15)      # Write digit to display
    
    # Increment counter
    ADDI x10, x10, 1
    
    # Check if done
    BLT x10, x11, loop
    
    HALT

# Usage examples:
# ./run.sh examples/clock_demo.asm --clock-hz 1      # 1 Hz - VERY slow (1 sec per instruction)
# ./run.sh examples/clock_demo.asm --clock-hz 10     # 10 Hz - slow (0.1 sec per instruction)
# ./run.sh examples/clock_demo.asm --clock-hz 100    # 100 Hz - visible (0.01 sec per instruction)
# ./run.sh examples/clock_demo.asm --clock-hz 1000   # 1 kHz - default (1 ms per instruction)
# ./run.sh examples/clock_demo.asm --no-clock        # Maximum speed (instant)
