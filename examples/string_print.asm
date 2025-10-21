# String printing demonstration
# Prints "Hello, World!" to the display

.data
hello_msg: .string "Hello, World!"
newline_msg: .string "\nWelcome to RISC VM!"

.text
main:
    # Print first string
    # Load address of hello_msg (0x10000) using LUI+ADDI
    LUI x10, 0x10               # Load upper 20 bits: 0x10000
    ADDI x10, x10, 0            # Add lower 12 bits: 0
    JAL x1, print_string        # Call print function
    
    # Print second string  
    # Address of newline_msg is 0x1000E (hello_msg + 14 bytes)
    LUI x10, 0x10               # Load upper 20 bits: 0x10000
    ADDI x10, x10, 14           # Add offset for second string
    JAL x1, print_string        # Call print function
    
    HALT                        # Stop execution

# Function: print_string
# Input: x10 = address of null-terminated string
# Uses: x11 (display pointer), x12 (character)
print_string:
    # Save return address on stack
    ADDI x2, x2, -4             # Allocate stack space
    SW x1, 0(x2)                # Save return address
    
    # Initialize display pointer to 0xF0000 (display buffer start)
    LUI x11, 0xF0               # Load upper 20 bits (0xF0000)
    
print_loop:
    LBU x12, 0(x10)             # Load byte from string
    BEQ x12, x0, print_done     # If null terminator, exit
    SB x12, 0(x11)              # Store byte to display
    ADDI x10, x10, 1            # Increment string pointer
    ADDI x11, x11, 1            # Increment display pointer
    JAL x0, print_loop          # Continue loop (unconditional jump)
    
print_done:
    # Restore return address and return
    LW x1, 0(x2)                # Restore return address
    ADDI x2, x2, 4              # Deallocate stack space
    JALR x0, x1, 0              # Return to caller
