# Hello World Program
# Writes "Hello, World!" to the memory-mapped display
# Now using character literals for improved readability!

.text
main:
    # Load display base address into x10
    LUI x10, 0xF0           # x10 = 0xF0000 (display buffer start)
    
    # Write 'H'
    ADDI x11, x0, 'H'
    SW x11, 0(x10)
    
    # Write 'e'
    ADDI x11, x0, 'e'
    SW x11, 4(x10)
    
    # Write 'l'
    ADDI x11, x0, 'l'
    SW x11, 8(x10)
    
    # Write 'l'
    ADDI x11, x0, 'l'
    SW x11, 12(x10)
    
    # Write 'o'
    ADDI x11, x0, 'o'
    SW x11, 16(x10)
    
    # Write ','
    ADDI x11, x0, ','
    SW x11, 20(x10)
    
    # Write ' ' (space)
    ADDI x11, x0, ' '
    SW x11, 24(x10)
    
    # Write 'W'
    ADDI x11, x0, 'W'
    SW x11, 28(x10)
    
    # Write 'o'
    ADDI x11, x0, 'o'
    SW x11, 32(x10)
    
    # Write 'r'
    ADDI x11, x0, 'r'
    SW x11, 36(x10)
    
    # Write 'l'
    ADDI x11, x0, 'l'
    SW x11, 40(x10)
    
    # Write 'd'
    ADDI x11, x0, 'd'
    SW x11, 44(x10)
    
    # Write '!'
    ADDI x11, x0, '!'
    SW x11, 48(x10)
    
    # Halt
    HALT
