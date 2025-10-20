# Real-Time Timer Test
# Tests the real-time timer at 10 Hz
# Counts 50 interrupts (5 seconds) then halts

.text
    # Initialize counter
    ADDI x10, x0, 0         # x10 = interrupt count
    
    # Set up interrupt handler (at instruction 17 = PC 68)
    ADDI x1, x0, 68         # Handler address
    CSRRW x0, 0x305, x1     # mtvec = handler address
    
    # Configure RT timer for 10 Hz (100ms intervals)
    LUI x1, 0xF8
    ADDI x1, x1, -480       # RT timer base 0xF7E20
    
    ADDI x2, x0, 10         # Frequency = 10 Hz
    SW x2, 4(x1)            # RT_TIMER_FREQUENCY
    
    ADDI x2, x0, 0x01       # Enable
    SW x2, 8(x1)            # RT_TIMER_CONTROL
    
    # Enable RT timer interrupt (bit 11 = 0x800)
    LUI x2, 0x0
    ADDI x2, x2, 0x800
    CSRRW x0, 0x304, x2     # mie = RT timer interrupt enable
    
    # Enable global interrupts
    ADDI x2, x0, 0x08
    CSRRW x0, 0x300, x2     # mstatus.MIE = 1
    
loop:
    # Check if we've had 50 interrupts (5 seconds at 10 Hz)
    ADDI x11, x0, 50
    BGE x10, x11, done
    JAL x0, loop
    
done:
    HALT

handler:
    # Increment counter
    ADDI x10, x10, 1
    
    # Clear RT timer interrupt
    LUI x1, 0xF8
    ADDI x1, x1, -480
    ADDI x2, x0, 0x05       # Enable | INT_PENDING
    SW x2, 8(x1)
    
    MRET
