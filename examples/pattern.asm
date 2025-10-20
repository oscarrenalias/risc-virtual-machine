# Pattern Display Demo
# Demonstrates memory-mapped display by creating a pattern

.text
main:
    # Load display base address
    LUI x10, 0xF0           # x10 = 0xF0000
    
    # Pattern: "***  RISC-VM  ***"
    
    # Write asterisks
    ADDI x11, x0, 42        # '*' = 42
    SW x11, 0(x10)
    SW x11, 4(x10)
    SW x11, 8(x10)
    
    # Space
    ADDI x11, x0, 32        # ' ' = 32
    SW x11, 12(x10)
    SW x11, 16(x10)
    
    # Write "RISC-VM"
    ADDI x11, x0, 82        # 'R'
    SW x11, 20(x10)
    ADDI x11, x0, 73        # 'I'
    SW x11, 24(x10)
    ADDI x11, x0, 83        # 'S'
    SW x11, 28(x10)
    ADDI x11, x0, 67        # 'C'
    SW x11, 32(x10)
    ADDI x11, x0, 45        # '-'
    SW x11, 36(x10)
    ADDI x11, x0, 86        # 'V'
    SW x11, 40(x10)
    ADDI x11, x0, 77        # 'M'
    SW x11, 44(x10)
    
    # More spaces
    ADDI x11, x0, 32        # ' '
    SW x11, 48(x10)
    SW x11, 52(x10)
    
    # More asterisks
    ADDI x11, x0, 42        # '*'
    SW x11, 56(x10)
    SW x11, 60(x10)
    SW x11, 64(x10)
    
    # Move to next line (80 chars * 4 bytes = 320 = 0x140)
    ADDI x10, x10, 320
    
    # Second line: "32-bit Architecture"
    ADDI x11, x0, 51        # '3'
    SW x11, 0(x10)
    ADDI x11, x0, 50        # '2'
    SW x11, 4(x10)
    ADDI x11, x0, 45        # '-'
    SW x11, 8(x10)
    ADDI x11, x0, 98        # 'b'
    SW x11, 12(x10)
    ADDI x11, x0, 105       # 'i'
    SW x11, 16(x10)
    ADDI x11, x0, 116       # 't'
    SW x11, 20(x10)
    ADDI x11, x0, 32        # ' '
    SW x11, 24(x10)
    ADDI x11, x0, 65        # 'A'
    SW x11, 28(x10)
    ADDI x11, x0, 114       # 'r'
    SW x11, 32(x10)
    ADDI x11, x0, 99        # 'c'
    SW x11, 36(x10)
    ADDI x11, x0, 104       # 'h'
    SW x11, 40(x10)
    
    HALT
