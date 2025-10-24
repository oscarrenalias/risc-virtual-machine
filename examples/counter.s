# Counter Program
# Counts from 0 to 9 and displays each number
# Uses RISC-V ABI register names

.text
main:
    # Initialize counter
    ADDI t0, zero, 0        # t0 = counter = 0
    ADDI t1, zero, 10       # t1 = limit = 10
    
    # Display base address
    LUI a0, 0xF0            # a0 = 0xF0000 (display buffer)
    
loop:
    # Check if done
    BEQ t0, t1, done
    
    # Convert counter to ASCII digit
    ADDI a1, t0, '0'        # a1 = counter + '0'
    
    # Write to display
    SW a1, 0(a0)
    
    # Increment counter and display position
    ADDI t0, t0, 1
    ADDI a0, a0, 4
    
    # Continue loop
    JAL zero, loop

done:
    HALT
