# Simple example demonstrating label support
# This shows how labels make code more maintainable

.text
main:
    # Set up interrupt handler using label
    LUI x1, 0x0
    ADDI x1, x1, my_handler       # No manual calculation needed!
    CSRRW x0, 0x305, x1           # Store in mtvec
    
    # Create a function pointer table
    ADDI x10, x0, func_a          # Function table[0] = func_a
    ADDI x11, x0, func_b          # Function table[1] = func_b
    ADDI x12, x0, func_c          # Function table[2] = func_c
    
    # Call a function indirectly
    JAL x1, func_a
    
    # Loop forever
    JAL x0, main

# Function A
func_a:
    ADDI x20, x20, 1
    JALR x0, x1, 0                # Return

# Function B
func_b:
    ADDI x21, x21, 1
    JALR x0, x1, 0                # Return

# Function C
func_c:
    ADDI x22, x22, 1
    JALR x0, x1, 0                # Return

# Interrupt handler
my_handler:
    ADDI x23, x23, 1
    MRET
