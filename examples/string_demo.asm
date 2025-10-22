# String printing demonstration - improved version (using ABI register names)
# Demonstrates string output with proper cursor tracking

.data
msg1: .string "Hello, World!"
msg2: .string "Welcome to RISC VM!"
msg3: .string "Strings work!"

.text
main:
    # Initialize display cursor at start of display (0xF0000)
    LUI s4, 0xF0                # s4 will track current display position
    
    # Print first string
    LA a0, msg1                 # Load address of msg1
    JAL ra, print_string
    
    # Print second string
    LA a0, msg2                 # Load address of msg2
    JAL ra, print_string
    
    # Print third string
    LA a0, msg3                 # Load address of msg3
    JAL ra, print_string
    
    HALT

# Function: print_string
# Input: a0 = address of null-terminated string
#        s4 = current display cursor position (updated by this function)
# Uses: a1 (temp char), a2 (display ptr copy)
print_string:
    # Save return address
    ADDI sp, sp, -4
    SW ra, 0(sp)
    
    # Copy display cursor to working register
    ADD a2, s4, zero            # a2 = current cursor position
    
print_loop:
    LBU a1, 0(a0)               # Load byte from string
    BEQ a1, zero, print_done    # If null, done
    SB a1, 0(a2)                # Write to display
    ADDI a0, a0, 1              # Next char in string
    ADDI a2, a2, 1              # Next display position
    JAL zero, print_loop
    
print_done:
    # Update global cursor position
    ADD s4, a2, zero            # s4 = final cursor position
    
    # Restore and return
    LW ra, 0(sp)
    ADDI sp, sp, 4
    JALR zero, ra, 0
