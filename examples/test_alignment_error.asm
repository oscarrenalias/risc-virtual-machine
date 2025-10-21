# Test program for unaligned memory access error
# This will trigger an alignment error

ADDI x5, x0, 0x10001  # Unaligned address (not 4-byte aligned)
LW x6, 0(x5)          # This should trigger: Unaligned memory access

HALT
