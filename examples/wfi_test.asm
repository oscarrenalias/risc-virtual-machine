# WFI (Wait For Interrupt) Test Program
# Tests the WFI instruction with timer interrupts
# Should count 5 timer interrupts then halt

.text
main:
    # Initialize counter
    ADDI x20, x0, 0         # x20 = interrupt counter
    ADDI x21, x0, 5         # x21 = target count (5 interrupts)
    
    # Set up timer interrupt handler using label
    LUI x1, 0x0
    ADDI x1, x1, timer_handler  # Handler address from label
    CSRRW x0, 0x305, x1         # mtvec = handler address
    
    # Configure cycle-based timer
    LUI x1, 0xF8
    ADDI x1, x1, -512       # Timer base = 0xF8000 - 512 = 0xF7E00
    
    # Set compare value to 100 cycles
    ADDI x3, x0, 100
    SW x3, 4(x1)            # Write to TIMER_COMPARE
    
    # Enable timer: periodic mode + auto-reload + enable
    ADDI x3, x0, 0x0B       # Bits: enable(1) | periodic(2) | auto-reload(8) = 0x0B
    SW x3, 8(x1)            # Write to TIMER_CONTROL
    
    # Enable timer interrupt in MIE
    ADDI x3, x0, 0x80       # Bit 7 = cycle-based timer
    CSRRW x0, 0x304, x3     # mie = timer interrupt enable
    
    # Enable global interrupts in mstatus
    ADDI x3, x0, 0x08
    CSRRW x0, 0x300, x3     # mstatus.MIE = 1

main_loop:
    # Use WFI instead of busy loop - much cleaner!
    WFI                     # Wait for next interrupt
    
    # Check if we've reached the target count
    BLT x20, x21, main_loop # If counter < target, keep waiting
    
    # Done - halt
    HALT

# Timer interrupt handler
timer_handler:
    # Increment counter
    ADDI x20, x20, 1
    
    # Clear timer interrupt pending bit
    LUI x1, 0xF8
    ADDI x1, x1, -512       # Timer base = 0xF8000 - 512 = 0xF7E00
    
    # Write control with pending bit set to clear it
    ADDI x3, x0, 0x0F       # All bits including pending(4)
    SW x3, 8(x1)            # Write to TIMER_CONTROL
    
    # Return from interrupt
    MRET
