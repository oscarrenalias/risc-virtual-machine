# WFI (Wait For Interrupt) Test Program
# Tests the WFI instruction with timer interrupts
# Should count 5 timer interrupts then halt
# Uses RISC-V ABI register names

.text
main:
    # Initialize counter
    ADDI s0, zero, 0        # s0 = interrupt counter
    ADDI s1, zero, 5        # s1 = target count (5 interrupts)
    
    # Set up timer interrupt handler using label
    LUI ra, 0x0
    ADDI ra, ra, timer_handler  # Handler address from label
    CSRRW zero, 0x305, ra       # mtvec = handler address
    
    # Configure cycle-based timer
    LUI a0, 0xF8
    ADDI a0, a0, -512       # Timer base = 0xF8000 - 512 = 0xF7E00
    
    # Set compare value to 100 cycles
    ADDI a1, zero, 100
    SW a1, 4(a0)            # Write to TIMER_COMPARE
    
    # Enable timer: periodic mode + auto-reload + enable
    ADDI a1, zero, 0x0B     # Bits: enable(1) | periodic(2) | auto-reload(8) = 0x0B
    SW a1, 8(a0)            # Write to TIMER_CONTROL
    
    # Enable timer interrupt in MIE
    ADDI a1, zero, 0x80     # Bit 7 = cycle-based timer
    CSRRW zero, 0x304, a1   # mie = timer interrupt enable
    
    # Enable global interrupts in mstatus
    ADDI a1, zero, 0x08
    CSRRW zero, 0x300, a1   # mstatus.MIE = 1

main_loop:
    # Use WFI instead of busy loop - much cleaner!
    WFI                     # Wait for next interrupt
    
    # Check if we've reached the target count
    BLT s0, s1, main_loop   # If counter < target, keep waiting
    
    # Done - halt
    HALT

# Timer interrupt handler
timer_handler:
    # Increment counter
    ADDI s0, s0, 1
    
    # Clear timer interrupt pending bit
    LUI a0, 0xF8
    ADDI a0, a0, -512       # Timer base = 0xF8000 - 512 = 0xF7E00
    
    # Write control with pending bit set to clear it
    ADDI a1, zero, 0x0F     # All bits including pending(4)
    SW a1, 8(a0)            # Write to TIMER_CONTROL
    
    # Return from interrupt
    MRET
