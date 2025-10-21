# String printing demonstration - improved version
# Demonstrates string output with proper cursor tracking

.data
msg1: .string "Hello, World!"
msg2: .string "Welcome to RISC VM!"
msg3: .string "Strings work!"

.text
main:
    # Initialize display cursor at start of display (0xF0000)
    LUI x20, 0xF0               # x20 will track current display position
    
    # Print first string
    LUI x10, 0x10               # Load address of msg1 (0x10000)
    ADDI x10, x10, 0
    JAL x1, print_string
    
    # Print second string
    LUI x10, 0x10               # Load address of msg2 (0x1000E = 0x10000 + 14)
    ADDI x10, x10, 14
    JAL x1, print_string
    
    # Print third string
    LUI x10, 0x10               # Load address of msg3 (0x10027 = 0x10000 + 39)
    ADDI x10, x10, 39
    JAL x1, print_string
    
    HALT

# Function: print_string
# Input: x10 = address of null-terminated string
#        x20 = current display cursor position (updated by this function)
# Uses: x11 (temp char), x12 (display ptr copy)
print_string:
    # Save return address
    ADDI x2, x2, -4
    SW x1, 0(x2)
    
    # Copy display cursor to working register
    ADD x12, x20, x0            # x12 = current cursor position
    
print_loop:
    LBU x11, 0(x10)             # Load byte from string
    BEQ x11, x0, print_done     # If null, done
    SB x11, 0(x12)              # Write to display
    ADDI x10, x10, 1            # Next char in string
    ADDI x12, x12, 1            # Next display position
    JAL x0, print_loop
    
print_done:
    # Update global cursor position
    ADD x20, x12, x0            # x20 = final cursor position
    
    # Restore and return
    LW x1, 0(x2)
    ADDI x2, x2, 4
    JALR x0, x1, 0
