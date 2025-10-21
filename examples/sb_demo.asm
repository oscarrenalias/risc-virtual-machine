# Example: Using SB (Store Byte) for display output
# This demonstrates that SB now works correctly with memory-mapped display

.text
main:
    # Load display base address (0xF0000)
    LUI x10, 0xF0           # x10 = 0xF0000 (display buffer base)
    
    # Write "HELLO" using SB (Store Byte)
    # With SB, positions are 1 byte apart
    
    ADDI x11, x0, 'H'
    SB x11, 0(x10)          # Position 0
    
    ADDI x11, x0, 'E'
    SB x11, 1(x10)          # Position 1
    
    ADDI x11, x0, 'L'
    SB x11, 2(x10)          # Position 2
    
    ADDI x11, x0, 'L'
    SB x11, 3(x10)          # Position 3
    
    ADDI x11, x0, 'O'
    SB x11, 4(x10)          # Position 4
    
    # Compare with SW (Store Word)
    # Write " WORLD" using SW - positions are 4 bytes apart
    
    ADDI x11, x0, ' '
    SW x11, 8(x10)          # Position 8 (skipping 5,6,7)
    
    ADDI x11, x0, 'W'
    SW x11, 12(x10)         # Position 12
    
    ADDI x11, x0, 'O'
    SW x11, 16(x10)         # Position 16
    
    ADDI x11, x0, 'R'
    SW x11, 20(x10)         # Position 20
    
    ADDI x11, x0, 'L'
    SW x11, 24(x10)         # Position 24
    
    ADDI x11, x0, 'D'
    SW x11, 28(x10)         # Position 28
    
    HALT
