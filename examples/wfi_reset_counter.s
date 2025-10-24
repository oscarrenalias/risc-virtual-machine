# WFI test with immediate interrupt
# Timer should fire almost immediately after WFI
# Uses RISC-V ABI register names

.text
main:
    # Set handler using label
    ADDI ra, zero, handler  # Handler address from label
    CSRRW zero, 0x305, ra
    
    # Setup timer - compare = 10 (we're at instruction 2, so 8 more to fire)
    LUI a0, 0xF8
    ADDI a0, a0, -512       # 0xF8000 - 512 = 0xF7E00
    ADDI a1, zero, 10
    SW a1, 4(a0)            # TIMER_COMPARE
    ADDI a1, zero, 0x0B
    SW a1, 8(a0)            # TIMER_CONTROL (enable)
    
    # Enable interrupts BEFORE enabling timer so we don't miss it
    ADDI a1, zero, 0x80
    CSRRW zero, 0x304, a1   # MIE
    ADDI a1, zero, 0x08
    CSRRW zero, 0x300, a1   # mstatus
    
    # At this point we've executed ~12 instructions
    # Timer will fire in -2 instructions (already passed!)
    # So let's reset the counter first
    LUI a0, 0xF8
    ADDI a0, a0, -512       # 0xF8000 - 512 = 0xF7E00
    ADDI a1, zero, 0
    SW a1, 0(a0)            # TIMER_COUNTER = 0
    
    # Now timer will fire in 10 instructions
    WFI
    HALT

handler:
    # Clear interrupt
    LUI a0, 0xF8
    ADDI a0, a0, -512
    ADDI a1, zero, 0x0F
    SW a1, 8(a0)
    MRET
