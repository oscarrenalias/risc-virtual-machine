# Test program for unaligned memory access error
# This will trigger an alignment error
# Uses RISC-V ABI register names

.text
main:
    ADDI t0, zero, 0x10001  # Unaligned address (not 4-byte aligned)
    LW t1, 0(t0)            # This should trigger: Unaligned memory access

    HALT
