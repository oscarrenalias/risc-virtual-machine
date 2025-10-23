# Minimal interrupt test - just setup, no loop
.text
    # Write handler address using label
    ADDI x1, x0, handler # Handler address
    CSRRW x0, 0x305, x1  # mtvec = handler address
    
    # Enable global interrupts
    ADDI x2, x0, 0x08    
    CSRRW x0, 0x300, x2  # mstatus.MIE = 1
    
    # Enable timer interrupt  
    ADDI x2, x0, 0x80    
    CSRRW x0, 0x304, x2  # mie = timer enable
    
    HALT

handler:
    HALT
