# Test Program
# Tests various instruction types
# Uses RISC-V ABI register names

.text
main:
    # Test arithmetic
    ADDI a0, zero, 10       # a0 = 10
    ADDI a1, zero, 20       # a1 = 20
    ADD a2, a0, a1          # a2 = 30
    SUB a3, a1, a0          # a3 = 10
    
    # Test logical operations
    ADDI t0, zero, 0xFF     # t0 = 255
    ANDI t1, t0, 0x0F       # t1 = 15
    ORI t2, t1, 0xF0        # t2 = 255
    
    # Test shifts
    ADDI t3, zero, 1
    SLLI t4, t3, 4          # t4 = 16
    SRLI t5, t4, 2          # t5 = 4
    
    # Test branches
    ADDI s0, zero, 5
    ADDI s1, zero, 5
    BEQ s0, s1, equal_branch
    ADDI s2, zero, 999      # Should not execute
    
equal_branch:
    ADDI s2, zero, 1        # s2 = 1 (branch taken)
    
    # Test memory operations
    LUI s3, 0x10            # s3 = 0x10000 (data segment)
    ADDI s4, zero, 42
    SW s4, 0(s3)            # Store 42 at 0x10000
    LW s5, 0(s3)            # Load back (s5 = 42)
    
    # Display success message
    LUI a0, 0xF0            # Display base
    ADDI a1, zero, 'O'
    SW a1, 0(a0)
    ADDI a1, zero, 'K'
    SW a1, 4(a0)
    
    HALT
