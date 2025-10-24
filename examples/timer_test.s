# Simple Timer Interrupt Test
# Just counts timer interrupts and halts after 5
# Uses RISC-V ABI register names

.text
main:
    # Initialize counter
    ADDI a0, zero, 0        # a0 = interrupt count
    
    # Set up interrupt handler using label
    ADDI ra, zero, handler  # Handler address
    CSRRW zero, 0x305, ra   # mtvec = handler address
    
    # Configure timer for 100 instruction intervals
    LUI s0, 0xF8            # Upper bits for 0x000F7E00
    ADDI s0, s0, -512       # 0xF8000 - 512 = 0xF7E00
    ADDI a1, zero, 100      # Compare = 100
    SW a1, 4(s0)            # TIMER_COMPARE
    
    ADDI a1, zero, 0x0B     # Enable|Periodic|AutoReload  
    SW a1, 8(s0)            # TIMER_CONTROL
    
    # Enable timer interrupt
    ADDI a1, zero, 0x80    
    CSRRW zero, 0x304, a1   # mie = timer interrupt enable
    
    # Enable global interrupts
    ADDI a1, zero, 0x08    
    CSRRW zero, 0x300, a1   # mstatus.MIE = 1
    
loop:
    # Check if we've had 5 interrupts
    ADDI a2, zero, 5
    BGE a0, a2, done
    JAL zero, loop
    
done:
    HALT

handler:
    # Increment counter
    ADDI a0, a0, 1
    
    # Clear interrupt - write all control bits back with pending bit to clear
    LUI s0, 0xF8
    ADDI s0, s0, -512       # Timer base 0xF7E00
    ADDI a1, zero, 0x0F     # Enable|Periodic|INT_PENDING|AutoReload  
    SW a1, 8(s0)            # Write-1-to-clear pending, maintain other bits
    
    MRET
