# Example: Using SB (Store Byte) for display output
# This demonstrates that SB now works correctly with memory-mapped display
# Uses RISC-V ABI register names and character literals

.text
main:
    # Load display base address (0xF0000)
    LUI a0, 0xF0            # a0 = 0xF0000 (display buffer base)
    
    # Write "HELLO" using SB (Store Byte)
    # With SB, positions are 1 byte apart
    
    ADDI a1, zero, 'H'
    SB a1, 0(a0)            # Position 0
    
    ADDI a1, zero, 'E'
    SB a1, 1(a0)            # Position 1
    
    ADDI a1, zero, 'L'
    SB a1, 2(a0)            # Position 2
    
    ADDI a1, zero, 'L'
    SB a1, 3(a0)            # Position 3
    
    ADDI a1, zero, 'O'
    SB a1, 4(a0)            # Position 4
    
    # Compare with SW (Store Word)
    # Write " WORLD" using SW - positions are 4 bytes apart
    
    ADDI a1, zero, ' '
    SW a1, 8(a0)            # Position 8 (skipping 5,6,7)
    
    ADDI a1, zero, 'W'
    SW a1, 12(a0)           # Position 12
    
    ADDI a1, zero, 'O'
    SW a1, 16(a0)           # Position 16
    
    ADDI a1, zero, 'R'
    SW a1, 20(a0)           # Position 20
    
    ADDI a1, zero, 'L'
    SW a1, 24(a0)           # Position 24
    
    ADDI a1, zero, 'D'
    SW a1, 28(a0)           # Position 28
    
    HALT
