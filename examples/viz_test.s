# Minimal test program for CPU visualization
# Just a few simple instructions to test the visualizer
# Uses RISC-V ABI register names and character literals

.text
main:
    # Load some values into registers
    ADDI t0, zero, 10       # t0 = 10
    ADDI t1, zero, 20       # t1 = 20
    ADD t2, t0, t1          # t2 = t0 + t1 = 30
    
    # Load display address
    LUI a0, 0xF0            # a0 = 0xF0000
    
    # Write 'Test' to display
    ADDI a1, zero, 'T'
    SW a1, 0(a0)
    
    ADDI a1, zero, 'e'
    SW a1, 4(a0)
    
    ADDI a1, zero, 's'
    SW a1, 8(a0)
    
    ADDI a1, zero, 't'
    SW a1, 12(a0)
    
    HALT
