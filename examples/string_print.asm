# String printing demonstration
# Prints "Hello, World!" to the display
# Uses ABI register names for clarity

.data
hello_msg: .string "Hello, World!"
newline_msg: .string "\nWelcome to RISC VM!"
positioned_msg: .string "At (10, 5)!"
corner_msg: .string "Corner"

.text
main:
    # Print first string at default position
    LA a0, hello_msg            # Load address of hello_msg (a0 = first argument)
    JAL ra, print_string        # Call print function (ra = return address)
    
    # Print second string at default position
    LA a0, newline_msg          # Load address of newline_msg
    JAL ra, print_string        # Call print function
    
    # Print string at specific coordinates (10, 5)
    LA a0, positioned_msg       # String address
    ADDI a1, zero, 10           # x = 10
    ADDI a2, zero, 5            # y = 5
    JAL ra, print_string_xy     # Call positioned print function
    
    # Print string at bottom-right corner (74, 24)
    LA a0, corner_msg           # String address
    ADDI a1, zero, 74           # x = 74 (80 - 6 chars)
    ADDI a2, zero, 24           # y = 24 (last row)
    JAL ra, print_string_xy     # Call positioned print function
    
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

# Function: print_string_xy
# Input: a0 = address of null-terminated string
#        a1 = x coordinate (0-79)
#        a2 = y coordinate (0-24)
# Uses: a3 (display pointer), a4 (character), t0 (temp for offset calculation)
# Display formula: offset = y * 80 + x
# Display buffer is at 0xF0000
print_string_xy:
    # Save return address and registers on stack
    ADDI sp, sp, -8             # Allocate stack space
    SW ra, 4(sp)                # Save return address
    SW a0, 0(sp)                # Save string pointer
    
    # Calculate display offset: y * 80 + x
    # t0 = y * 80
    ADDI t0, zero, 80           # Load 80 into t0
    MUL t0, a2, t0              # t0 = y * 80
    ADD t0, t0, a1              # t0 = y * 80 + x
    
    # Initialize display pointer to 0xF0000 (display buffer start)
    LUI a3, 0xF0                # Load upper 20 bits (0xF0000)
    ADD a3, a3, t0              # Add offset to display base
    
    # Restore string pointer
    LW a0, 0(sp)                # Restore string pointer
    
print_xy_loop:
    LBU a4, 0(a0)               # Load byte from string
    BEQ a4, zero, print_xy_done # If null terminator, exit
    SB a4, 0(a3)                # Store byte to display
    ADDI a0, a0, 1              # Increment string pointer
    ADDI a3, a3, 1              # Increment display pointer
    JAL zero, print_xy_loop     # Continue loop
    
print_xy_done:
    # Restore return address and return
    LW ra, 4(sp)                # Restore return address
    ADDI sp, sp, 8              # Deallocate stack space
    JALR zero, ra, 0            # Return to caller
