# Test program to trigger various exceptions for testing error reporting
# This program intentionally causes memory access errors
# Uses RISC-V ABI register names

.text
main:
    # Set up some registers
    ADDI t0, zero, 10       # t0 = 10
    ADDI t1, zero, 20       # t1 = 20

    # Try to access invalid memory (out of bounds)
    LUI t2, 0x10000         # t2 = 0x10000000 (way out of bounds)
    LW t3, 0(t2)            # This should trigger: Memory access out of bounds

    HALT
