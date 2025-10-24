# WFI Deadlock Test
# This program intentionally creates a deadlock by using WFI with interrupts disabled
# Should trigger the timeout protection mechanism
# Uses RISC-V ABI register names

.text
main:
    # Disable global interrupts (this will cause deadlock)
    ADDI a0, zero, 0
    CSRRW zero, 0x300, a0   # mstatus.MIE = 0
    
    # Try to wait for interrupt (will deadlock since interrupts are disabled)
    WFI
    
    # Should never reach here due to timeout
    HALT
