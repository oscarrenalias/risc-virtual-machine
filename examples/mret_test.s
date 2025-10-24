# Test MRET instruction
# Uses RISC-V ABI register names

.text
main:
    # Save current PC to mepc 
    ADDI ra, zero, 20           # Return address (instruction 5)
    CSRRW zero, 0x341, ra       # mepc = 20
    
    # Enable interrupts in mstatus
    ADDI a0, zero, 0x08
    CSRRW zero, 0x300, a0       # mstatus.MIE = 1
    
    # Now execute MRET - should jump to address 20 and re-enable interrupts
    MRET
    
    # Should skip this
    HALT
    
    # Should land here (address 20, instruction 5)
    HALT
