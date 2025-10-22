# Simple CALL/RET Demo
# Demonstrates basic function call and return using CALL/RET pseudo-instructions
# Compares old style (JAL/JALR) with new style (CALL/RET)

.text
main:
    # Initialize display
    lui s0, 0xF0            # s0 = display base address (0xF0000)
    
    # Example 1: Simple function call
    addi a0, zero, 'H'
    addi a1, zero, 0        # Position 0
    CALL print_char         # Much cleaner than: JAL ra, print_char
    
    addi a0, zero, 'i'
    addi a1, zero, 4        # Position 4 (1 char * 4 bytes)
    CALL print_char
    
    addi a0, zero, '!'
    addi a1, zero, 8        # Position 8
    CALL print_char
    
    # Example 2: Function that returns a value
    addi a0, zero, 10
    addi a1, zero, 20
    CALL add_numbers
    # Result is in a0 (should be 30)
    
    # Display the result at position 12
    addi a1, zero, 12
    CALL print_char
    
    HALT

# print_char: Display a character at given position
# Input:  a0 = character to print
#         a1 = position offset (in bytes)
#         s0 = display base address
# Output: none
# This is a "leaf function" - does not call other functions
# so we do not need to save ra
print_char:
    add t0, s0, a1          # Calculate display address
    sw a0, 0(t0)            # Store character
    RET                     # Much cleaner than: JALR zero, ra, 0

# add_numbers: Add two numbers
# Input:  a0 = first number
#         a1 = second number
# Output: a0 = sum
# Another leaf function
add_numbers:
    add a0, a0, a1          # a0 = a0 + a1
    RET

# For comparison, here's how it would look without CALL/RET:
# 
# OLD STYLE (using JAL/JALR):
# main_old:
#     addi a0, zero, 'H'
#     JAL ra, print_char_old
#     HALT
# 
# print_char_old:
#     sw a0, 0(s0)
#     JALR zero, ra, 0
#
# NEW STYLE (using CALL/RET):
# main_new:
#     addi a0, zero, 'H'
#     CALL print_char_new
#     HALT
#
# print_char_new:
#     sw a0, 0(s0)
#     RET
#
# Much more readable!
