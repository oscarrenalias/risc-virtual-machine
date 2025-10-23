# Prime Number Checker
# Uses MUL, DIV, and REM to check if a number is prime
# Uses RISC-V ABI register names for clarity

# Number to check (change this to test different numbers)
ADDI a0, zero, 17       # Number to test (17 is prime)

# Handle special cases
ADDI a1, zero, 2
BLT a0, a1, not_prime   # Numbers < 2 are not prime

BEQ a0, a1, is_prime    # 2 is prime

# Check if even (divisible by 2)
REM a2, a0, a1
BEQ a2, zero, not_prime # If remainder is 0, not prime

# Check odd divisors from 3 to sqrt(n)
ADDI t0, zero, 3        # Current divisor
ADDI t1, zero, 2        # Increment by 2 (check odd numbers only)

check_loop:
    # Check if divisor^2 > n (using multiplication)
    MUL t2, t0, t0      # t2 = divisor^2
    BLT a0, t2, is_prime # If n < divisor^2, we're done (is prime)
    
    # Check if n is divisible by current divisor
    REM t3, a0, t0      # t3 = n % divisor
    BEQ t3, zero, not_prime # If remainder is 0, not prime
    
    # Move to next odd divisor
    ADD t0, t0, t1      # divisor += 2
    JAL zero, check_loop

is_prime:
    # Display "PRIME" on screen
    LUI s0, 0xF0        # Display base address
    ADDI s1, zero, 80   # ASCII 'P'
    SW s1, 0(s0)
    ADDI s1, zero, 82   # ASCII 'R'
    SW s1, 4(s0)
    ADDI s1, zero, 73   # ASCII 'I'
    SW s1, 8(s0)
    ADDI s1, zero, 77   # ASCII 'M'
    SW s1, 12(s0)
    ADDI s1, zero, 69   # ASCII 'E'
    SW s1, 16(s0)
    JAL zero, done

not_prime:
    # Display "NOT PRIME" on screen
    LUI s0, 0xF0        # Display base address
    ADDI s1, zero, 78   # ASCII 'N'
    SW s1, 0(s0)
    ADDI s1, zero, 79   # ASCII 'O'
    SW s1, 4(s0)
    ADDI s1, zero, 84   # ASCII 'T'
    SW s1, 8(s0)
    ADDI s1, zero, 32   # ASCII space
    SW s1, 12(s0)
    ADDI s1, zero, 80   # ASCII 'P'
    SW s1, 16(s0)
    ADDI s1, zero, 82   # ASCII 'R'
    SW s1, 20(s0)
    ADDI s1, zero, 73   # ASCII 'I'
    SW s1, 24(s0)
    ADDI s1, zero, 77   # ASCII 'M'
    SW s1, 28(s0)
    ADDI s1, zero, 69   # ASCII 'E'
    SW s1, 32(s0)

done:
    HALT
