# Minimal interrupt test - just setup, no loop
.text
    # Write handler address directly 
    ADDI x1, x0, 32      # Handler at instruction 8 = byte 32
    CSRRW x0, 0x305, x1  # mtvec = 32
    
    # Enable global interrupts
    ADDI x2, x0, 0x08    
    CSRRW x0, 0x300, x2  # mstatus.MIE = 1
    
    # Enable timer interrupt  
    ADDI x2, x0, 0x80    
    CSRRW x0, 0x304, x2  # mie = timer enable
    
    HALT

handler:
    HALT
