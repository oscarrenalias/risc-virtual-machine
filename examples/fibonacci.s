# Fibonacci Sequence Calculator
# Calculates first N Fibonacci numbers and displays them
# Uses RISC-V ABI register names for clarity

.text
main:
    # Initialize Fibonacci sequence
    ADDI t0, zero, 0        # t0 = fib(0) = 0
    ADDI t1, zero, 1        # t1 = fib(1) = 1
    ADDI t2, zero, 10       # t2 = counter (calculate 10 numbers)
    
    # Display base address
    LUI a0, 0xF0            # a0 = 0xF0000 (display buffer)
    ADDI a1, zero, 0        # a1 = display offset
    
fib_loop:
    # Check if done
    BEQ t2, zero, done
    
    # Display current Fibonacci number (t0)
    # Convert to ASCII digit (only works for 0-9)
    ADDI a2, t0, '0'        # Add ASCII '0'
    ADD a3, a0, a1          # Calculate display address
    SW a2, 0(a3)            # Write to display
    
    # Add space
    ADDI a1, a1, 4
    ADDI a2, zero, ' '      # Space character
    ADD a3, a0, a1
    SW a2, 0(a3)
    
    # Calculate next Fibonacci number
    ADD t3, t0, t1          # t3 = fib(n) + fib(n-1)
    ADDI t0, t1, 0          # t0 = old t1
    ADDI t1, t3, 0          # t1 = new fib
    
    # Increment offset and decrement counter
    ADDI a1, a1, 4
    ADDI t2, t2, -1
    
    JAL zero, fib_loop

done:
    HALT
