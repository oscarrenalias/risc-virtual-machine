# Clock example with label-based addressing
# Demonstrates using labels instead of manually calculated addresses

.text
main:
    # Initialize time to 00:00:00
    ADDI x20, x0, 0         # x20 = hours
    ADDI x21, x0, 0         # x21 = minutes
    ADDI x22, x0, 0         # x22 = seconds
    
    # Load display base address
    LUI x10, 0xF0           # x10 = 0xF0000 (display buffer base)

    # Set up real-time timer interrupt handler
    # Instead of: ADDI x1, x1, 380  (manual calculation)
    # We can now use: ADDI x1, x1, timer_handler (automatic!)
    LUI x1, 0x0
    ADDI x1, x1, timer_handler    # Handler address - no manual calculation!
    CSRRW x0, 0x305, x1           # mtvec = handler address
    
    # Configure real-time timer for 1 Hz
    LUI x1, 0xF8
    ADDI x1, x1, -480       # RT timer base = 0xF8000 - 480 = 0xF7E20
    
    ADDI x3, x0, 1          # Frequency = 1 Hz
    SW x3, 4(x1)            # Write to RT_TIMER_FREQUENCY
    
    ADDI x3, x0, 0x01       # Enable bit
    SW x3, 8(x1)            # Write to RT_TIMER_CONTROL
    
    # Enable real-time timer interrupt in MIE (bit 11 = 0x800)
    LUI x3, 0x1             # Load 0x1000
    ADDI x3, x3, -2048      # Subtract 2048 to get 0x800
    CSRRW x0, 0x304, x3     # mie = RT timer interrupt enable
    
    # Enable global interrupts in mstatus
    ADDI x3, x0, 0x08
    CSRRW x0, 0x300, x3     # mstatus.MIE = 1
    
    # Display initial clock
    CALL display_clock

main_loop:
    # Main loop - wait for interrupts using WFI
    WFI                     # Wait for next timer interrupt
    JAL x0, main_loop       # Loop back - no manual address calculation!

# Display clock subroutine
display_clock:
    # Save return address
    ADDI sp, sp, -4
    SW x1, 0(sp)
    
    # Display hours
    ADDI x11, x0, 30        # Row 30
    ADDI x12, x0, 38        # Column 38 (centered)
    ADD x13, x0, x20        # Value = hours
    
    # Hours tens digit
    ADDI x14, x0, 10
    DIVU x15, x13, x14      # Divide by 10
    ADDI x15, x15, 48       # Add ASCII '0'
    
    # Call helper to display digit (inlined here for simplicity)
    JAL x0, div_h_tens      # Branch to digit display logic

div_h_tens:
    # Display hours tens digit at (30, 38)
    # Calculate offset: (row * 80 + col) * 4 (word-aligned)
    ADDI x16, x0, 80
    MUL x17, x11, x16       # row * 80
    ADD x17, x17, x12       # + col
    ADDI x18, x0, 4
    MUL x17, x17, x18       # * 4 for word alignment
    ADD x17, x17, x10       # + display base
    SW x15, 0(x17)
    
    # Hours ones digit
    ADDI x12, x12, 1        # Next column
    REMU x15, x13, x14      # Modulo 10
    ADDI x15, x15, 48       # Add ASCII '0'
    JAL x0, div_m_tens

div_m_tens:
    # Display hours ones digit
    MUL x17, x11, x16
    ADD x17, x17, x12
    MUL x17, x17, x18       # * 4 for word alignment
    ADD x17, x17, x10
    SW x15, 0(x17)
    
    # Display colon
    ADDI x12, x12, 1
    ADDI x15, x0, 58        # ASCII ':'
    JAL x0, div_s_tens

div_s_tens:
    MUL x17, x11, x16
    ADD x17, x17, x12
    MUL x17, x17, x18       # * 4 for word alignment
    ADD x17, x17, x10
    SW x15, 0(x17)
    
    # Minutes tens digit
    ADDI x12, x12, 1
    ADD x13, x0, x21        # Value = minutes
    DIVU x15, x13, x14
    ADDI x15, x15, 48
    
    MUL x17, x11, x16
    ADD x17, x17, x12
    MUL x17, x17, x18       # * 4 for word alignment
    ADD x17, x17, x10
    SW x15, 0(x17)
    
    # Minutes ones digit
    ADDI x12, x12, 1
    REMU x15, x13, x14
    ADDI x15, x15, 48
    
    MUL x17, x11, x16
    ADD x17, x17, x12
    MUL x17, x17, x18       # * 4 for word alignment
    ADD x17, x17, x10
    SW x15, 0(x17)
    
    # Display colon
    ADDI x12, x12, 1
    ADDI x15, x0, 58
    
    MUL x17, x11, x16
    ADD x17, x17, x12
    MUL x17, x17, x18       # * 4 for word alignment
    ADD x17, x17, x10
    SW x15, 0(x17)
    
    # Seconds tens digit
    ADDI x12, x12, 1
    ADD x13, x0, x22        # Value = seconds
    DIVU x15, x13, x14
    ADDI x15, x15, 48
    
    MUL x17, x11, x16
    ADD x17, x17, x12
    MUL x17, x17, x18       # * 4 for word alignment
    ADD x17, x17, x10
    SW x15, 0(x17)
    
    # Seconds ones digit
    ADDI x12, x12, 1
    REMU x15, x13, x14
    ADDI x15, x15, 48
    
    MUL x17, x11, x16
    ADD x17, x17, x12
    MUL x17, x17, x18       # * 4 for word alignment
    ADD x17, x17, x10
    SW x15, 0(x17)
    
    # Restore return address and return
    LW x1, 0(sp)
    ADDI sp, sp, 4
    RET

# Real-time timer interrupt handler
timer_handler:
    # Increment seconds
    ADDI x22, x22, 1
    
    # Check if seconds >= 60
    ADDI x4, x0, 60
    BLT x22, x4, timer_update    # If x22 < 60, skip to update
    
    # Reset seconds and increment minutes
    ADDI x22, x0, 0
    ADDI x21, x21, 1
    
    # Check if minutes >= 60
    BLT x21, x4, timer_update    # If x21 < 60, skip to update
    
    # Reset minutes and increment hours
    ADDI x21, x0, 0
    ADDI x20, x20, 1
    
    # Check if hours >= 24
    ADDI x4, x0, 24
    BLT x20, x4, timer_update    # If x20 < 24, skip to update
    
    # Reset hours
    ADDI x20, x0, 0

timer_update:
    # Update display - using label instead of manual calculation!
    CALL display_clock
    
    # Return from interrupt
    MRET
