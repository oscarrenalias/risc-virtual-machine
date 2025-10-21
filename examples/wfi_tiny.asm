# Tiny WFI test - timer fires after just 5 cycles
.text
main:
    # Set handler using label
    ADDI x1, x0, handler    # Handler address from label
    CSRRW x0, 0x305, x1
    
    # Setup timer
    LUI x1, 0xF8
    ADDI x1, x1, -512       # 0xF8000 - 512 = 0xF7E00
    
    # Compare = 20 (after our setup instructions)
    ADDI x3, x0, 20
    SW x3, 4(x1)
    
    # Control = 0x0B
    ADDI x3, x0, 0x0B
    SW x3, 8(x1)
    
    # Enable timer interrupt (MIE bit 7 = 0x80)
    ADDI x3, x0, 0x80
    CSRRW x0, 0x304, x3
    
    # Enable global interrupts
    ADDI x3, x0, 0x08
    CSRRW x0, 0x300, x3
    
    WFI
    HALT

handler:
    # Clear interrupt
    LUI x1, 0xF8
    ADDI x1, x1, -512
    ADDI x3, x0, 0x0F
    SW x3, 8(x1)
    MRET
