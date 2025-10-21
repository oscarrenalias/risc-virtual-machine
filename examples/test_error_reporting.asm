# Test program to trigger various exceptions for testing error reporting
# This program intentionally causes memory access errors

# Set up some registers
ADDI x5, x0, 10       # x5 = 10
ADDI x6, x0, 20       # x6 = 20

# Try to access invalid memory (out of bounds)
LUI x7, 0x10000       # x7 = 0x10000000 (way out of bounds)
LW x8, 0(x7)          # This should trigger: Memory access out of bounds

HALT
