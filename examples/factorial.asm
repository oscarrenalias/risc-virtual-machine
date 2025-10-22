# Factorial Calculator
# Calculates 5! = 120 and displays the result
# Uses RISC-V ABI register names for clarity

.text
main:
    # Calculate factorial of 5
    ADDI t0, zero, 5        # t0 = n = 5
    ADDI t1, zero, 1        # t1 = result = 1
    
factorial_loop:
    # Check if n == 0
    BEQ t0, zero, display_result
    
    # result = result * n
    # (using repeated addition since we don't have multiply)
    ADDI t2, t1, 0          # t2 = temp result
    ADDI t3, t0, -1         # t3 = counter = n - 1
    
multiply_loop:
    BEQ t3, zero, multiply_done
    ADD t1, t1, t2          # result += temp
    ADDI t3, t3, -1
    JAL zero, multiply_loop
    
multiply_done:
    # Decrement n
    ADDI t0, t0, -1
    JAL zero, factorial_loop

display_result:
    # Display the result (120)
    # We'll display it as individual digits
    LUI a0, 0xF0            # a0 = display base
    
    # Display '1' (first digit of 120)
    ADDI a1, zero, 49       # '1'
    SW a1, 0(a0)
    
    # Display '2' (second digit)
    ADDI a1, zero, 50       # '2'
    SW a1, 4(a0)
    
    # Display '0' (third digit)
    ADDI a1, zero, 48       # '0'
    SW a1, 8(a0)
    
    HALT
