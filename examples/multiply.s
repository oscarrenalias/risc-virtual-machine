# Multiplication Examples
# Demonstrates the MUL instruction from the M-extension

# Simple multiplication: 6 * 7 = 42
ADDI x1, x0, 6
ADDI x2, x0, 7
MUL x3, x1, x2          # x3 = 42

# Calculate area of rectangle: width * height
ADDI x10, x0, 12        # width = 12
ADDI x11, x0, 8         # height = 8
MUL x12, x10, x11       # area = 96

# Power of 2: 2^5 = 32
ADDI x20, x0, 2         # base = 2
ADDI x21, x0, 1         # result = 1
ADDI x22, x0, 5         # exponent = 5
ADDI x23, x0, 0         # counter = 0

power_loop:
    BEQ x23, x22, power_done
    MUL x21, x21, x20   # result *= base
    ADDI x23, x23, 1    # counter++
    JAL x0, power_loop

power_done:
    # x21 now contains 32

# Display result on screen
LUI x28, 0xF0           # Display base address (0xF0000)
ADDI x29, x0, 51        # ASCII '3'
SW x29, 0(x28)          # Store at 0xF0000 + 0
ADDI x29, x0, 50        # ASCII '2'
SW x29, 4(x28)          # Store at 0xF0000 + 4
ADDI x29, x0, 32        # ASCII space
SW x29, 8(x28)          # Store at 0xF0000 + 8
ADDI x29, x0, 40        # ASCII '('
SW x29, 12(x28)         # Store at 0xF0000 + 12
ADDI x29, x0, 50        # ASCII '2'
SW x29, 16(x28)         # Store at 0xF0000 + 16
ADDI x29, x0, 94        # ASCII '^'
SW x29, 20(x28)         # Store at 0xF0000 + 20
ADDI x29, x0, 53        # ASCII '5'
SW x29, 24(x28)         # Store at 0xF0000 + 24
ADDI x29, x0, 41        # ASCII ')'
SW x29, 28(x28)         # Store at 0xF0000 + 28

HALT
