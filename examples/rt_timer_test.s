# Real-Time Timer Test
# Tests the real-time timer at 10 Hz
# Counts 50 interrupts (5 seconds) then halts
# Uses RISC-V ABI register names

.text
main:
    # Initialize counter
    ADDI a0, zero, 0        # a0 = interrupt count
    
    # Set up interrupt handler using label
    ADDI ra, zero, handler  # Handler address from label
    CSRRW zero, 0x305, ra   # mtvec = handler address
    
    # Configure RT timer for 10 Hz (100ms intervals)
    LUI s0, 0xF8
    ADDI s0, s0, -480       # RT timer base 0xF7E20
    
    ADDI a1, zero, 10       # Frequency = 10 Hz
    SW a1, 4(s0)            # RT_TIMER_FREQUENCY
    
    ADDI a1, zero, 0x01     # Enable
    SW a1, 8(s0)            # RT_TIMER_CONTROL
    
    # Enable RT timer interrupt (bit 11 = 0x800)
    LUI a1, 0x0
    ADDI a1, a1, 0x800
    CSRRW zero, 0x304, a1   # mie = RT timer interrupt enable
    
    # Enable global interrupts
    ADDI a1, zero, 0x08
    CSRRW zero, 0x300, a1   # mstatus.MIE = 1
    
loop:
    # Check if we've had 50 interrupts (5 seconds at 10 Hz)
    ADDI a2, zero, 50
    BGE a0, a2, done
    JAL zero, loop
    
done:
    HALT

handler:
    # Increment counter
    ADDI a0, a0, 1
    
    # Clear RT timer interrupt
    LUI s0, 0xF8
    ADDI s0, s0, -480
    ADDI a1, zero, 0x05     # Enable | INT_PENDING
    SW a1, 8(s0)
    
    MRET
