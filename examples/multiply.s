# Multiplication Examples
# Demonstrates the MUL instruction from the M-extension
# Uses RISC-V ABI register names and character literals

.text
main:
    # Simple multiplication: 6 * 7 = 42
    ADDI a0, zero, 6
    ADDI a1, zero, 7
    MUL a2, a0, a1          # a2 = 42

    # Calculate area of rectangle: width * height
    ADDI s0, zero, 12       # width = 12
    ADDI s1, zero, 8        # height = 8
    MUL s2, s0, s1          # area = 96

    # Power of 2: 2^5 = 32
    ADDI t0, zero, 2        # base = 2
    ADDI t1, zero, 1        # result = 1
    ADDI t2, zero, 5        # exponent = 5
    ADDI t3, zero, 0        # counter = 0

power_loop:
    BEQ t3, t2, power_done
    MUL t1, t1, t0          # result *= base
    ADDI t3, t3, 1          # counter++
    JAL zero, power_loop

power_done:
    # t1 now contains 32

    # Display result on screen: "32 (2^5)"
    LUI a0, 0xF0            # Display base address (0xF0000)
    ADDI a1, zero, '3'
    SW a1, 0(a0)
    ADDI a1, zero, '2'
    SW a1, 4(a0)
    ADDI a1, zero, ' '
    SW a1, 8(a0)
    ADDI a1, zero, '('
    SW a1, 12(a0)
    ADDI a1, zero, '2'
    SW a1, 16(a0)
    ADDI a1, zero, '^'
    SW a1, 20(a0)
    ADDI a1, zero, '5'
    SW a1, 24(a0)
    ADDI a1, zero, ')'
    SW a1, 28(a0)

    HALT
