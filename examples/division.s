# Division and Remainder Examples
# Demonstrates DIV, DIVU, REM, REMU instructions from the M-extension
# Uses RISC-V ABI register names and character literals

.text
main:
    # Simple division: 42 / 7 = 6
    ADDI a0, zero, 42
    ADDI a1, zero, 7
    DIV a2, a0, a1          # a2 = 6 (quotient)
    REM a3, a0, a1          # a3 = 0 (remainder)

    # Division with remainder: 23 / 5 = 4 remainder 3
    ADDI s0, zero, 23
    ADDI s1, zero, 5
    DIV s2, s0, s1          # s2 = 4 (quotient)
    REM s3, s0, s1          # s3 = 3 (remainder)

    # Verify: dividend = quotient * divisor + remainder
    MUL s4, s2, s1          # s4 = 4 * 5 = 20
    ADD s4, s4, s3          # s4 = 20 + 3 = 23 ✓

    # Test signed division with negative numbers
    ADDI t0, zero, -20
    ADDI t1, zero, 4
    DIV t2, t0, t1          # t2 = -5 (signed)
    REM t3, t0, t1          # t3 = 0

    # Test unsigned division (treats -1 as large positive)
    ADDI t4, zero, -1       # t4 = 0xFFFFFFFF (4294967295)
    ADDI t5, zero, 2
    DIVU t6, t4, t5         # t6 = 2147483647 (0x7FFFFFFF)
    REMU a4, t4, t5         # a4 = 1

    # Display "DIV OK" on screen
    LUI a0, 0xF0            # Display base address
    ADDI a1, zero, 'D'
    SW a1, 0(a0)
    ADDI a1, zero, 'I'
    SW a1, 4(a0)
    ADDI a1, zero, 'V'
    SW a1, 8(a0)
    ADDI a1, zero, ' '
    SW a1, 12(a0)
    ADDI a1, zero, 'O'
    SW a1, 16(a0)
    ADDI a1, zero, 'K'
    SW a1, 20(a0)

    HALT
