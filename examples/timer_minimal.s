# Minimal interrupt test - just setup, no loop
# Uses RISC-V ABI register names

.text
main:
    # Write handler address using label
    ADDI ra, zero, handler  # Handler address
    CSRRW zero, 0x305, ra   # mtvec = handler address
    
    # Enable global interrupts
    ADDI a0, zero, 0x08    
    CSRRW zero, 0x300, a0   # mstatus.MIE = 1
    
    # Enable timer interrupt  
    ADDI a0, zero, 0x80    
    CSRRW zero, 0x304, a0   # mie = timer enable
    
    HALT

handler:
    HALT
