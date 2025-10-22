# Hello World Program
# Writes "Hello, World!" to the memory-mapped display
# Uses character literals and RISC-V ABI register names

.text
main:
    # Load display base address into a0
    LUI a0, 0xF0            # a0 = 0xF0000 (display buffer start)
    
    # Write 'H'
    ADDI a1, zero, 'H'
    SW a1, 0(a0)
    
    # Write 'e'
    ADDI a1, zero, 'e'
    SW a1, 4(a0)
    
    # Write 'l'
    ADDI a1, zero, 'l'
    SW a1, 8(a0)
    
    # Write 'l'
    ADDI a1, zero, 'l'
    SW a1, 12(a0)
    
    # Write 'o'
    ADDI a1, zero, 'o'
    SW a1, 16(a0)
    
    # Write ','
    ADDI a1, zero, ','
    SW a1, 20(a0)
    
    # Write ' ' (space)
    ADDI a1, zero, ' '
    SW a1, 24(a0)
    
    # Write 'W'
    ADDI a1, zero, 'W'
    SW a1, 28(a0)
    
    # Write 'o'
    ADDI a1, zero, 'o'
    SW a1, 32(a0)
    
    # Write 'r'
    ADDI a1, zero, 'r'
    SW a1, 36(a0)
    
    # Write 'l'
    ADDI a1, zero, 'l'
    SW a1, 40(a0)
    
    # Write 'd'
    ADDI a1, zero, 'd'
    SW a1, 44(a0)
    
    # Write '!'
    ADDI a1, zero, '!'
    SW a1, 48(a0)
    
    # Halt
    HALT
