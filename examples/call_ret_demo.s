# CALL and RET Pseudo-Instructions Demo
# Demonstrates the new CALL and RET pseudo-instructions
# which make function calls more readable

# This program calculates factorial of 5 using recursive function calls
# and displays the result on screen

.text
main:
    # Initialize display base address (0xF0000)
    lui s0, 0xF0            # s0 = display base address
    
    # Calculate factorial(5)
    addi a0, zero, 5        # Argument: n = 5
    CALL factorial          # Call factorial function
    
    # Result is in a0, display it
    # For simplicity, just display the numeric value as characters
    CALL display_number
    
    HALT

# factorial: Calculate n! recursively
# Input:  a0 = n
# Output: a0 = n!
# Uses:   s1 (must preserve), ra (must save for recursion)
factorial:
    # Base case: if n <= 1, return 1
    addi t0, zero, 2
    blt a0, t0, factorial_base  # if n < 2, return 1
    
    # Recursive case: n * factorial(n-1)
    # Save registers we need to preserve
    addi sp, sp, -8
    sw ra, 0(sp)            # Save return address (for nested calls)
    sw a0, 4(sp)            # Save current n
    
    # Calculate factorial(n-1)
    addi a0, a0, -1         # a0 = n - 1
    CALL factorial          # Recursive call
    
    # Multiply result by n
    lw t0, 4(sp)            # Restore n into t0
    mul a0, a0, t0          # a0 = factorial(n-1) * n
    
    # Restore saved registers
    lw ra, 0(sp)            # Restore return address
    addi sp, sp, 8          # Deallocate stack space
    RET

factorial_base:
    # Base case: return 1
    addi a0, zero, 1
    RET

# display_number: Display a number on screen
# Input:  a0 = number to display
#         s0 = display base address
# Output: none
# Uses:   t0-t3 (temporary, don't need to preserve)
display_number:
    # Save registers we'll use
    addi sp, sp, -4
    sw s1, 0(sp)
    
    # For demo purposes, convert number to digits and display
    # We'll display at position 0, simple approach
    
    # Save the number
    addi s1, a0, 0
    
    # Display "Result: "
    addi a0, zero, 'R'
    sw a0, 0(s0)
    addi a0, zero, 'e'
    sw a0, 4(s0)
    addi a0, zero, 's'
    sw a0, 8(s0)
    addi a0, zero, 'u'
    sw a0, 12(s0)
    addi a0, zero, 'l'
    sw a0, 16(s0)
    addi a0, zero, 't'
    sw a0, 20(s0)
    addi a0, zero, ':'
    sw a0, 24(s0)
    addi a0, zero, ' '
    sw a0, 28(s0)
    
    # Convert number to ASCII and display
    # Simple approach: assume result < 1000
    addi t2, zero, 32       # Current display offset
    
    # Get hundreds digit
    addi t0, zero, 100
    div t1, s1, t0          # t1 = number / 100
    rem s1, s1, t0          # s1 = number % 100
    
    # Display hundreds (if non-zero)
    beq t1, zero, skip_hundreds
    addi t1, t1, 48         # Convert to ASCII ('0' = 48)
    add t3, s0, t2          # Calculate display address
    sw t1, 0(t3)
    addi t2, t2, 4          # Move to next position

skip_hundreds:
    # Get tens digit
    addi t0, zero, 10
    div t1, s1, t0          # t1 = number / 10
    rem s1, s1, t0          # s1 = number % 10
    
    # Display tens
    addi t1, t1, 48         # Convert to ASCII
    add t3, s0, t2
    sw t1, 0(t3)
    addi t2, t2, 4
    
    # Display ones
    addi t1, s1, 48         # Convert to ASCII
    add t3, s0, t2
    sw t1, 0(t3)
    
    # Restore and return
    lw s1, 0(sp)
    addi sp, sp, 4
    RET


# Example of multiple helper functions
# These demonstrate typical function call patterns

# helper1: Simple helper that calls another function
helper1:
    # Save ra because we're calling another function
    addi sp, sp, -4
    sw ra, 0(sp)
    
    CALL helper2
    
    # Do something with result
    addi a0, a0, 10
    
    lw ra, 0(sp)
    addi sp, sp, 4
    RET

# helper2: Leaf function (doesn't call others)
# Leaf functions don't need to save ra
helper2:
    # Just do some computation
    addi a0, zero, 42
    RET

# print_char: Print a single character to display
# Input:  a0 = character to print
#         a1 = display offset (in bytes)
#         s0 = display base address
# Output: none
print_char:
    # Calculate address
    add t0, s0, a1
    sw a0, 0(t0)
    RET

# clear_screen: Fill screen with spaces
# Input:  s0 = display base address
# Output: none
# Uses:   t0-t2
clear_screen:
    addi t0, zero, 0        # Current offset
    addi t1, zero, 2000     # 80x25 = 2000 chars
    slli t1, t1, 2          # Convert to bytes (x4)
    addi t2, zero, 32       # Space character

clear_loop:
    bge t0, t1, clear_done
    add t3, s0, t0
    sw t2, 0(t3)
    addi t0, t0, 4
    jal zero, clear_loop    # Jump back (use JAL with zero to discard return address)

clear_done:
    RET
