# Division and Remainder Examples
# Demonstrates DIV, DIVU, REM, REMU instructions from the M-extension

# Simple division: 42 / 7 = 6
ADDI x1, x0, 42
ADDI x2, x0, 7
DIV x3, x1, x2          # x3 = 6 (quotient)
REM x4, x1, x2          # x4 = 0 (remainder)

# Division with remainder: 23 / 5 = 4 remainder 3
ADDI x10, x0, 23
ADDI x11, x0, 5
DIV x12, x10, x11       # x12 = 4 (quotient)
REM x13, x10, x11       # x13 = 3 (remainder)

# Verify: dividend = quotient * divisor + remainder
MUL x14, x12, x11       # x14 = 4 * 5 = 20
ADD x14, x14, x13       # x14 = 20 + 3 = 23 ✓

# Test signed division with negative numbers
ADDI x20, x0, -20
ADDI x21, x0, 4
DIV x22, x20, x21       # x22 = -5 (signed)
REM x23, x20, x21       # x23 = 0

# Test unsigned division (treats -1 as large positive)
ADDI x24, x0, -1        # x24 = 0xFFFFFFFF (4294967295)
ADDI x25, x0, 2
DIVU x26, x24, x25      # x26 = 2147483647 (0x7FFFFFFF)
REMU x27, x24, x25      # x27 = 1

# Display "DIV OK" on screen
LUI x28, 0xF0           # Display base address
ADDI x29, x0, 68        # ASCII 'D'
SW x29, 0(x28)
ADDI x29, x0, 73        # ASCII 'I'
SW x29, 4(x28)
ADDI x29, x0, 86        # ASCII 'V'
SW x29, 8(x28)
ADDI x29, x0, 32        # ASCII space
SW x29, 12(x28)
ADDI x29, x0, 79        # ASCII 'O'
SW x29, 16(x28)
ADDI x29, x0, 75        # ASCII 'K'
SW x29, 20(x28)

HALT
