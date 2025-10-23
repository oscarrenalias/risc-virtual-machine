# WFI Deadlock Test
# This program intentionally creates a deadlock by using WFI with interrupts disabled
# Should trigger the timeout protection mechanism

.text
main:
    # Disable global interrupts (this will cause deadlock)
    ADDI x3, x0, 0
    CSRRW x0, 0x300, x3     # mstatus.MIE = 0
    
    # Try to wait for interrupt (will deadlock since interrupts are disabled)
    WFI
    
    # Should never reach here due to timeout
    HALT
