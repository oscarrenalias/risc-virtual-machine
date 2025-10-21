# Minimal test program for CPU visualization
# Just a few simple instructions to test the visualizer

.text
main:
    # Load some values into registers
    ADDI x5, x0, 10         # x5 = 10
    ADDI x6, x0, 20         # x6 = 20
    ADD x7, x5, x6          # x7 = x5 + x6 = 30
    
    # Load display address
    LUI x10, 0xF0           # x10 = 0xF0000
    
    # Write 'T' to display
    ADDI x11, x0, 84        # 'T'
    SW x11, 0(x10)
    
    # Write 'e' to display  
    ADDI x11, x0, 101       # 'e'
    SW x11, 4(x10)
    
    # Write 's' to display
    ADDI x11, x0, 115       # 's'
    SW x11, 8(x10)
    
    # Write 't' to display
    ADDI x11, x0, 116       # 't'
    SW x11, 12(x10)
    
    HALT
