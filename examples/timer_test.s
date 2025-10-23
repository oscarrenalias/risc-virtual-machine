# Simple Timer Interrupt Test
# Just counts timer interrupts and halts after 5

.text
    # Initialize counter
    ADDI x10, x0, 0      # x10 = interrupt count
    
    # Set up interrupt handler using label
    ADDI x1, x0, handler # Handler address
    CSRRW x0, 0x305, x1  # mtvec = handler address
    
    # Configure timer for 100 instruction intervals
    LUI x1, 0xF8         # Upper bits for 0x000F7E00
    ADDI x1, x1, -512    # 0xF8000 - 512 = 0xF7E00
    ADDI x2, x0, 100     # Compare = 100
    SW x2, 4(x1)         # TIMER_COMPARE
    
    ADDI x2, x0, 0x0B    # Enable|Periodic|AutoReload  
    SW x2, 8(x1)         # TIMER_CONTROL
    
    # Enable timer interrupt
    ADDI x2, x0, 0x80    
    CSRRW x0, 0x304, x2  # mie = timer interrupt enable
    
    # Enable global interrupts
    ADDI x2, x0, 0x08    
    CSRRW x0, 0x300, x2  # mstatus.MIE = 1
    
loop:
    # Check if we've had 5 interrupts
    ADDI x11, x0, 5
    BGE x10, x11, done
    JAL x0, loop
    
done:
    HALT

handler:
    # Increment counter
    ADDI x10, x10, 1
    
    # Clear interrupt - write all control bits back with pending bit to clear
    LUI x1, 0xF8
    ADDI x1, x1, -512    # Timer base 0xF7E00
    ADDI x2, x0, 0x0F    # Enable|Periodic|INT_PENDING|AutoReload  
    SW x2, 8(x1)         # Write-1-to-clear pending, maintain other bits
    
    MRET
