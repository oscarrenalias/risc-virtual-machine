# Demo program for J (Jump) pseudo-instruction
# Shows unconditional jumps with the J instruction

.text
main:
    # Example 1: Simple jump
    ADDI a0, zero, 1      # Set a0 = 1
    J skip1               # Jump over next instruction
    ADDI a0, zero, 999    # This will be skipped
    
skip1:
    # a0 should still be 1
    
    # Example 2: Conditional logic with J
    ADDI a1, zero, 10     # a1 = 10
    ADDI a2, zero, 20     # a2 = 20
    
    BLT a1, a2, is_less   # Branch if a1 < a2
    ADDI a3, zero, 0      # Set result to 0 (a1 >= a2)
    J check_done          # Jump to end
    
is_less:
    ADDI a3, zero, 1      # Set result to 1 (a1 < a2)
    
check_done:
    # a3 should be 1 (since 10 < 20)
    
    # Example 3: Jump to end (like an early return)
    ADDI a4, zero, 5
    J end                 # Jump directly to end
    ADDI a4, zero, 100    # Never executed
    
end:
    # a4 should be 5
    HALT

# Note: J is different from CALL
# - J does not save a return address (writes to zero register)
# - CALL saves the return address in ra for use with RET
# - Use J for unconditional jumps, CALL for function calls
