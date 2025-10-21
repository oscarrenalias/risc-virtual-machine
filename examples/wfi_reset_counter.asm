# WFI test with immediate interrupt
# Timer should fire almost immediately after WFI

.text
main:
    # Set handler using label
    ADDI x1, x0, handler    # Handler address from label
    CSRRW x0, 0x305, x1
    
    # Setup timer - compare = 10 (we're at instruction 2, so 8 more to fire)
    LUI x1, 0xF8
    ADDI x1, x1, -512       # 0xF8000 - 512 = 0xF7E00
    ADDI x3, x0, 10
    SW x3, 4(x1)            # TIMER_COMPARE
    ADDI x3, x0, 0x0B
    SW x3, 8(x1)            # TIMER_CONTROL (enable)
    
    # Enable interrupts BEFORE enabling timer so we don't miss it
    ADDI x3, x0, 0x80
    CSRRW x0, 0x304, x3     # MIE
    ADDI x3, x0, 0x08
    CSRRW x0, 0x300, x3     # mstatus
    
    # At this point we've executed ~12 instructions
    # Timer will fire in -2 instructions (already passed!)
    # So let's reset the counter first
    LUI x1, 0xF8
    ADDI x1, x1, -512       # 0xF8000 - 512 = 0xF7E00
    ADDI x3, x0, 0
    SW x3, 0(x1)            # TIMER_COUNTER = 0
    
    # Now timer will fire in 10 instructions
    WFI
    HALT

handler:
    # Clear interrupt
    LUI x1, 0xF8
    ADDI x1, x1, -512
    ADDI x3, x0, 0x0F
    SW x3, 8(x1)
    MRET
