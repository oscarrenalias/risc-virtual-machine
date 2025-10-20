# Counter Program
# Counts from 0 to 9 and displays each number

.text
main:
    # Initialize counter
    ADDI x5, x0, 0          # x5 = counter = 0
    ADDI x6, x0, 10         # x6 = limit = 10
    
    # Display base address
    LUI x10, 0xF0           # x10 = 0xF0000
    
loop:
    # Check if done
    BEQ x5, x6, done
    
    # Convert counter to ASCII digit
    ADDI x11, x5, 48        # x11 = counter + '0'
    
    # Write to display
    SW x11, 0(x10)
    
    # Increment counter and display position
    ADDI x5, x5, 1
    ADDI x10, x10, 4
    
    # Continue loop
    JAL x0, loop

done:
    HALT
