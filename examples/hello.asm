# Hello World Program
# Writes "Hello, World!" to the memory-mapped display

.text
main:
    # Load display base address into x10
    LUI x10, 0xF0           # x10 = 0xF0000 (display buffer start)
    
    # Write 'H' (72)
    ADDI x11, x0, 72
    SW x11, 0(x10)
    
    # Write 'e' (101)
    ADDI x11, x0, 101
    SW x11, 4(x10)
    
    # Write 'l' (108)
    ADDI x11, x0, 108
    SW x11, 8(x10)
    
    # Write 'l' (108)
    ADDI x11, x0, 108
    SW x11, 12(x10)
    
    # Write 'o' (111)
    ADDI x11, x0, 111
    SW x11, 16(x10)
    
    # Write ',' (44)
    ADDI x11, x0, 44
    SW x11, 20(x10)
    
    # Write ' ' (32)
    ADDI x11, x0, 32
    SW x11, 24(x10)
    
    # Write 'W' (87)
    ADDI x11, x0, 87
    SW x11, 28(x10)
    
    # Write 'o' (111)
    ADDI x11, x0, 111
    SW x11, 32(x10)
    
    # Write 'r' (114)
    ADDI x11, x0, 114
    SW x11, 36(x10)
    
    # Write 'l' (108)
    ADDI x11, x0, 108
    SW x11, 40(x10)
    
    # Write 'd' (100)
    ADDI x11, x0, 100
    SW x11, 44(x10)
    
    # Write '!' (33)
    ADDI x11, x0, 33
    SW x11, 48(x10)
    
    # Halt
    HALT
