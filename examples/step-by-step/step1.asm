# Step by step code: print a character in position 0,0 on the screen

.text
main:
    # Load display base address (0xF0000)
    LUI x10, 0xF0           # x10 = 0xF0000 (display buffer base)
    
    # Load ASCII code for 'A'
    ADDI x11, x0, 'A'
    
    # Write to position (0,0) - offset 0
    # Note: Both SB and SW work for display output
    # SB writes a single byte, SW writes 4 bytes
    SB x11, 0(x10)          # Store 'A' at display[0]

    # Load next character
    ADDI x11, x0, 'B'
    
    # Write to position (0,1) - one word after (0,0)
    # Using SW, each position is 4 bytes apart (word-aligned)
    SB x11, 1(x10)          # Store 'B' at display[1]
    
    # Stop execution
    HALT