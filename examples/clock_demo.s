# CPU Clock Speed Demo
# This program demonstrates the impact of CPU clock frequency
# Counts from 0 to 9 and displays each number
# Uses RISC-V ABI register names and character literals

# Display numbers 0-9
# Best viewed with live display: ./run.sh -l examples/clock_demo.s

.text
main:
    ADDI a0, zero, 0        # Counter starts at 0
    ADDI a1, zero, 10       # Max count = 10
    ADDI a2, zero, 0xF0000  # Display buffer base

loop:
    # Write counter to display
    ADDI t0, a0, '0'        # Convert to ASCII ('0' + counter)
    
    # Calculate display position (counter * 4 for spacing)
    ADD t1, a0, a0          # t1 = counter * 2
    ADD t1, t1, t1          # t1 = counter * 4
    ADD t2, a2, t1          # t2 = display base + offset
    
    SB t0, 0(t2)            # Write digit to display
    
    # Increment counter
    ADDI a0, a0, 1
    
    # Check if done
    BLT a0, a1, loop
    
    HALT

# Usage examples:
# ./run.sh examples/clock_demo.s --clock-hz 1      # 1 Hz - VERY slow (1 sec per instruction)
# ./run.sh examples/clock_demo.s --clock-hz 10     # 10 Hz - slow (0.1 sec per instruction)
# ./run.sh examples/clock_demo.s --clock-hz 100    # 100 Hz - visible (0.01 sec per instruction)
# ./run.sh examples/clock_demo.s --clock-hz 1000   # 1 kHz - default (1 ms per instruction)
# ./run.sh examples/clock_demo.s --no-clock        # Maximum speed (instant)
