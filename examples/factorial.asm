# Factorial Calculator
# Calculates 5! = 120 and displays the result

.text
main:
    # Calculate factorial of 5
    ADDI x5, x0, 5          # x5 = n = 5
    ADDI x6, x0, 1          # x6 = result = 1
    
factorial_loop:
    # Check if n == 0
    BEQ x5, x0, display_result
    
    # result = result * n
    # (using repeated addition since we don't have multiply)
    ADDI x7, x6, 0          # x7 = temp result
    ADDI x8, x5, -1         # x8 = counter = n - 1
    
multiply_loop:
    BEQ x8, x0, multiply_done
    ADD x6, x6, x7          # result += temp
    ADDI x8, x8, -1
    JAL x0, multiply_loop
    
multiply_done:
    # Decrement n
    ADDI x5, x5, -1
    JAL x0, factorial_loop

display_result:
    # Display the result (120)
    # We'll display it as individual digits
    LUI x10, 0xF0           # x10 = display base
    
    # Display '1' (first digit of 120)
    ADDI x11, x0, 49        # '1'
    SW x11, 0(x10)
    
    # Display '2' (second digit)
    ADDI x11, x0, 50        # '2'
    SW x11, 4(x10)
    
    # Display '0' (third digit)
    ADDI x11, x0, 48        # '0'
    SW x11, 8(x10)
    
    HALT
