# Simple example demonstrating label support
# This shows how labels make code more maintainable
# Uses RISC-V ABI register names

.text
main:
    # Set up interrupt handler using label
    LUI ra, 0x0
    ADDI ra, ra, my_handler         # No manual calculation needed!
    CSRRW zero, 0x305, ra           # Store in mtvec
    
    # Create a function pointer table
    ADDI a0, zero, func_a           # Function table[0] = func_a
    ADDI a1, zero, func_b           # Function table[1] = func_b
    ADDI a2, zero, func_c           # Function table[2] = func_c
    
    # Call a function indirectly
    CALL func_a
    
    # Loop forever
    JAL zero, main

# Function A
func_a:
    ADDI s0, s0, 1
    RET

# Function B
func_b:
    ADDI s1, s1, 1
    RET

# Function C
func_c:
    ADDI s2, s2, 1
    RET

# Interrupt handler
my_handler:
    ADDI s3, s3, 1
    MRET
