# Test Program
# Tests various instruction types

.text
main:
    # Test arithmetic
    ADDI x1, x0, 10         # x1 = 10
    ADDI x2, x0, 20         # x2 = 20
    ADD x3, x1, x2          # x3 = 30
    SUB x4, x2, x1          # x4 = 10
    
    # Test logical operations
    ADDI x5, x0, 0xFF       # x5 = 255
    ANDI x6, x5, 0x0F       # x6 = 15
    ORI x7, x6, 0xF0        # x7 = 255
    
    # Test shifts
    ADDI x8, x0, 1
    SLLI x9, x8, 4          # x9 = 16
    SRLI x10, x9, 2         # x10 = 4
    
    # Test branches
    ADDI x11, x0, 5
    ADDI x12, x0, 5
    BEQ x11, x12, equal_branch
    ADDI x13, x0, 999       # Should not execute
    
equal_branch:
    ADDI x13, x0, 1         # x13 = 1 (branch taken)
    
    # Test memory operations
    LUI x14, 0x10           # x14 = 0x10000 (data segment)
    ADDI x15, x0, 42
    SW x15, 0(x14)          # Store 42 at 0x10000
    LW x16, 0(x14)          # Load back (x16 = 42)
    
    # Display success message
    LUI x20, 0xF0           # Display base
    ADDI x21, x0, 79        # 'O'
    SW x21, 0(x20)
    ADDI x21, x0, 75        # 'K'
    SW x21, 4(x20)
    
    HALT
