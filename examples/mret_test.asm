# Test MRET instruction
.text
    # Save current PC to mepc 
    ADDI x1, x0, 20      # Return address (instruction 5)
    CSRRW x0, 0x341, x1  # mepc = 20
    
    # Enable interrupts in mstatus
    ADDI x2, x0, 0x08
    CSRRW x0, 0x300, x2  # mstatus.MIE = 1
    
    # Now execute MRET - should jump to address 20 and re-enable interrupts
    MRET
    
    # Should skip this
    HALT
    
    # Should land here (address 20, instruction 5)
    HALT
