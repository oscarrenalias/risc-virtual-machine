# Prime Number Checker
# Uses MUL, DIV, and REM to check if a number is prime

# Number to check (change this to test different numbers)
ADDI x1, x0, 17         # Number to test (17 is prime)

# Handle special cases
ADDI x2, x0, 2
BLT x1, x2, not_prime   # Numbers < 2 are not prime

BEQ x1, x2, is_prime    # 2 is prime

# Check if even (divisible by 2)
REM x3, x1, x2
BEQ x3, x0, not_prime   # If remainder is 0, not prime

# Check odd divisors from 3 to sqrt(n)
ADDI x4, x0, 3          # Current divisor
ADDI x5, x0, 2          # Increment by 2 (check odd numbers only)

check_loop:
    # Check if divisor^2 > n (using multiplication)
    MUL x6, x4, x4      # x6 = divisor^2
    BLT x1, x6, is_prime # If n < divisor^2, we're done (is prime)
    
    # Check if n is divisible by current divisor
    REM x7, x1, x4      # x7 = n % divisor
    BEQ x7, x0, not_prime # If remainder is 0, not prime
    
    # Move to next odd divisor
    ADD x4, x4, x5      # divisor += 2
    JAL x0, check_loop

is_prime:
    # Display "PRIME" on screen
    LUI x28, 0xF0       # Display base address
    ADDI x29, x0, 80    # ASCII 'P'
    SW x29, 0(x28)
    ADDI x29, x0, 82    # ASCII 'R'
    SW x29, 4(x28)
    ADDI x29, x0, 73    # ASCII 'I'
    SW x29, 8(x28)
    ADDI x29, x0, 77    # ASCII 'M'
    SW x29, 12(x28)
    ADDI x29, x0, 69    # ASCII 'E'
    SW x29, 16(x28)
    JAL x0, done

not_prime:
    # Display "NOT PRIME" on screen
    LUI x28, 0xF0       # Display base address
    ADDI x29, x0, 78    # ASCII 'N'
    SW x29, 0(x28)
    ADDI x29, x0, 79    # ASCII 'O'
    SW x29, 4(x28)
    ADDI x29, x0, 84    # ASCII 'T'
    SW x29, 8(x28)
    ADDI x29, x0, 32    # ASCII space
    SW x29, 12(x28)
    ADDI x29, x0, 80    # ASCII 'P'
    SW x29, 16(x28)
    ADDI x29, x0, 82    # ASCII 'R'
    SW x29, 20(x28)
    ADDI x29, x0, 73    # ASCII 'I'
    SW x29, 24(x28)
    ADDI x29, x0, 77    # ASCII 'M'
    SW x29, 28(x28)
    ADDI x29, x0, 69    # ASCII 'E'
    SW x29, 32(x28)

done:
    HALT
