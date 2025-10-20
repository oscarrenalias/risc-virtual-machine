# Fibonacci Sequence Calculator
# Calculates first N Fibonacci numbers and displays them

.text
main:
    # Initialize Fibonacci sequence
    ADDI x5, x0, 0          # x5 = fib(0) = 0
    ADDI x6, x0, 1          # x6 = fib(1) = 1
    ADDI x7, x0, 10         # x7 = counter (calculate 10 numbers)
    
    # Display base address
    LUI x10, 0xF0           # x10 = 0xF0000
    ADDI x11, x0, 0         # x11 = display offset
    
fib_loop:
    # Check if done
    BEQ x7, x0, done
    
    # Display current Fibonacci number (x5)
    # Convert to ASCII digit (only works for 0-9)
    ADDI x12, x5, 48        # Add ASCII '0'
    ADD x13, x10, x11       # Calculate display address
    SW x12, 0(x13)          # Write to display
    
    # Add space
    ADDI x11, x11, 4
    ADDI x12, x0, 32        # Space character
    ADD x13, x10, x11
    SW x12, 0(x13)
    
    # Calculate next Fibonacci number
    ADD x8, x5, x6          # x8 = fib(n) + fib(n-1)
    ADDI x5, x6, 0          # x5 = old x6
    ADDI x6, x8, 0          # x6 = new fib
    
    # Increment offset and decrement counter
    ADDI x11, x11, 4
    ADDI x7, x7, -1
    
    JAL x0, fib_loop

done:
    HALT
