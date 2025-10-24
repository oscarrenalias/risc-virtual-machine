# Test program to show stack usage and then trigger write protection error
# This demonstrates better stack state in the error report
# Uses RISC-V ABI register names

.text
main:
    # Push some values onto the stack
    ADDI t0, zero, 100      # t0 = 100
    ADDI sp, sp, -4         # Move SP down (allocate 4 bytes)
    SW t0, 0(sp)            # Store value on stack

    ADDI t1, zero, 200      # t1 = 200
    ADDI sp, sp, -4         # Allocate more
    SW t1, 0(sp)            # Store another value

    ADDI t2, zero, 300      # t2 = 300
    ADDI sp, sp, -4         # Allocate more
    SW t2, 0(sp)            # Store another value

    # Now try to write to text segment (should fail with protection enabled)
    ADDI t3, zero, 0        # t3 = 0 (text segment address)
    SW t0, 0(t3)            # This should trigger: Memory Protection Violation

    HALT
