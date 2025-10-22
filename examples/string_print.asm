# String printing demonstration
# Prints "Hello, World!" to the display
# Uses ABI register names for clarity

.data
hello_msg: .string "Hello, World!"
newline_msg: .string "\nWelcome to RISC VM!"

.text
main:
    # Print first string
    LA a0, hello_msg            # Load address of hello_msg (a0 = first argument)
    JAL ra, print_string        # Call print function (ra = return address)
    
    # Print second string  
    LA a0, newline_msg          # Load address of newline_msg
    JAL ra, print_string        # Call print function
    
    HALT                        # Stop execution

# Function: print_string
# Input: a0 = address of null-terminated string
# Uses: a1 (display pointer), a2 (character)
print_string:
    # Save return address on stack
    ADDI sp, sp, -4             # Allocate stack space (sp = stack pointer)
    SW ra, 0(sp)                # Save return address
    
    # Initialize display pointer to 0xF0000 (display buffer start)
    LUI a1, 0xF0                # Load upper 20 bits (0xF0000)
    
print_loop:
    LBU a2, 0(a0)               # Load byte from string
    BEQ a2, zero, print_done    # If null terminator, exit (zero = x0)
    SB a2, 0(a1)                # Store byte to display
    ADDI a0, a0, 1              # Increment string pointer
    ADDI a1, a1, 1              # Increment display pointer
    JAL zero, print_loop        # Continue loop (unconditional jump)
    
print_done:
    # Restore return address and return
    LW ra, 0(sp)                # Restore return address
    ADDI sp, sp, 4              # Deallocate stack space
    JALR zero, ra, 0            # Return to caller
