# Tiny WFI test - timer fires after just 20 cycles
# Uses RISC-V ABI register names

.text
main:
    # Set handler using label
    ADDI ra, zero, handler      # Handler address from label
    CSRRW zero, 0x305, ra
    
    # Setup timer
    LUI a0, 0xF8
    ADDI a0, a0, -512           # 0xF8000 - 512 = 0xF7E00
    
    # Compare = 20 (after our setup instructions)
    ADDI a1, zero, 20
    SW a1, 4(a0)
    
    # Control = 0x0B
    ADDI a1, zero, 0x0B
    SW a1, 8(a0)
    
    # Enable timer interrupt (MIE bit 7 = 0x80)
    ADDI a1, zero, 0x80
    CSRRW zero, 0x304, a1
    
    # Enable global interrupts
    ADDI a1, zero, 0x08
    CSRRW zero, 0x300, a1
    
    WFI
    HALT

handler:
    # Clear interrupt
    LUI a0, 0xF8
    ADDI a0, a0, -512
    ADDI a1, zero, 0x0F
    SW a1, 8(a0)
    MRET
