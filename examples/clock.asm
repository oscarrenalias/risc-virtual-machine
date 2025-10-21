# Digital Clock - Real-time clock display
# Displays time in HH:MM:SS format in the center of the screen
# Uses real-time timer interrupt at 1 Hz to update every second

.text
main:
    # Initialize time to 00:00:00
    ADDI x20, x0, 0         # x20 = hours
    ADDI x21, x0, 0         # x21 = minutes
    ADDI x22, x0, 0         # x22 = seconds
    
    # Load display base address
    LUI x10, 0xF0           # x10 = 0xF0000 (display buffer base)

    # Set up real-time timer interrupt handler
    LUI x1, 0x0
    ADDI x1, x1, timer_handler    # Handler address - using label!
    CSRRW x0, 0x305, x1           # mtvec = handler address
    
    # Configure real-time timer for 1 Hz
    LUI x1, 0xF8
    ADDI x1, x1, -480       # RT timer base = 0xF8000 - 480 = 0xF7E20
    
    ADDI x3, x0, 1          # Frequency = 1 Hz (use x3 instead of x2)
    SW x3, 4(x1)            # Write to RT_TIMER_FREQUENCY
    
    ADDI x3, x0, 0x01       # Enable bit
    SW x3, 8(x1)            # Write to RT_TIMER_CONTROL
    
    # Enable real-time timer interrupt in MIE (bit 11 = 0x800)
    # Note: 0x800 is negative in 12-bit signed, so use LUI to load upper bits
    LUI x3, 0x1             # Load 0x1000
    ADDI x3, x3, -2048      # Subtract 2048 to get 0x800 (clearer than sign extension)
    CSRRW x0, 0x304, x3     # mie = RT timer interrupt enable
    
    # Enable global interrupts in mstatus
    ADDI x3, x0, 0x08
    CSRRW x0, 0x300, x3     # mstatus.MIE = 1
    
    # Display initial clock
    JAL x1, display_clock

main_loop:
    # Main loop - wait for interrupts using WFI (power efficient!)
    WFI                     # Wait for next timer interrupt
    JAL x0, main_loop       # Loop back to wait again

# Display clock subroutine
display_clock:
    # Save return address
    ADDI x2, x2, -4
    SW x1, 0(x2)
    
    # Clear the clock line (row 12, centered)
    ADDI x11, x10, 3840
    ADDI x11, x11, 560      # Center position
    
    # Display hours (tens digit)
    ADDI x12, x20, 0        # Copy hours
    ADDI x13, x0, 10        # Divisor
    ADDI x14, x0, 0         # Counter
div_h_tens:
    BLT x12, x13, done_h_tens
    SUB x12, x12, x13
    ADDI x14, x14, 1
    JAL x0, div_h_tens
done_h_tens:
    ADDI x14, x14, 48       # Convert to ASCII
    SW x14, 0(x11)
    ADDI x12, x12, 48       # Hours ones digit
    SW x12, 4(x11)
    
    # Colon
    ADDI x14, x0, 58
    SW x14, 8(x11)
    
    # Display minutes (tens digit)
    ADDI x12, x21, 0
    ADDI x14, x0, 0
div_m_tens:
    BLT x12, x13, done_m_tens
    SUB x12, x12, x13
    ADDI x14, x14, 1
    JAL x0, div_m_tens
done_m_tens:
    ADDI x14, x14, 48
    SW x14, 12(x11)
    ADDI x12, x12, 48       # Minutes ones digit
    SW x12, 16(x11)
    
    # Colon
    ADDI x14, x0, 58
    SW x14, 20(x11)
    
    # Display seconds (tens digit)
    ADDI x12, x22, 0
    ADDI x14, x0, 0
div_s_tens:
    BLT x12, x13, done_s_tens
    SUB x12, x12, x13
    ADDI x14, x14, 1
    JAL x0, div_s_tens
done_s_tens:
    ADDI x14, x14, 48
    SW x14, 24(x11)
    ADDI x12, x12, 48       # Seconds ones digit
    SW x12, 28(x11)
    
    # Display title "REAL-TIME CLOCK"
    ADDI x11, x10, 3200     # Row 10
    ADDI x11, x11, 512      # Center title
    
    ADDI x14, x0, 82        # 'R'
    SW x14, 0(x11)
    ADDI x14, x0, 69        # 'E'
    SW x14, 4(x11)
    ADDI x14, x0, 65        # 'A'
    SW x14, 8(x11)
    ADDI x14, x0, 76        # 'L'
    SW x14, 12(x11)
    ADDI x14, x0, 45        # '-'
    SW x14, 16(x11)
    ADDI x14, x0, 84        # 'T'
    SW x14, 20(x11)
    ADDI x14, x0, 73        # 'I'
    SW x14, 24(x11)
    ADDI x14, x0, 77        # 'M'
    SW x14, 28(x11)
    ADDI x14, x0, 69        # 'E'
    SW x14, 32(x11)
    ADDI x14, x0, 32        # ' '
    SW x14, 36(x11)
    ADDI x14, x0, 67        # 'C'
    SW x14, 40(x11)
    ADDI x14, x0, 76        # 'L'
    SW x14, 44(x11)
    ADDI x14, x0, 79        # 'O'
    SW x14, 48(x11)
    ADDI x14, x0, 67        # 'C'
    SW x14, 52(x11)
    ADDI x14, x0, 75        # 'K'
    SW x14, 56(x11)
    
    # Restore return address and return
    LW x1, 0(x2)
    ADDI x2, x2, 4
    JALR x0, x1, 0

# Real-time timer interrupt handler
timer_handler:
    # Save registers
    ADDI x2, x2, -32
    SW x10, 0(x2)
    SW x11, 4(x2)
    SW x12, 8(x2)
    SW x13, 12(x2)
    SW x14, 16(x2)
    SW x1, 20(x2)
    
    # Increment seconds
    ADDI x22, x22, 1
    ADDI x13, x0, 60
    BLT x22, x13, update_display
    
    # Seconds overflow - increment minutes
    ADDI x22, x0, 0
    ADDI x21, x21, 1
    BLT x21, x13, update_display
    
    # Minutes overflow - increment hours
    ADDI x21, x0, 0
    ADDI x20, x20, 1
    ADDI x13, x0, 24
    BLT x20, x13, update_display
    
    # Hours overflow - reset to 00:00:00
    ADDI x20, x0, 0

update_display:
    # Update the display
    JAL x1, display_clock
    
    # Clear RT timer interrupt
    LUI x11, 0xF8
    ADDI x11, x11, -480     # RT timer base = 0xF8000 - 480 = 0xF7E20
    ADDI x12, x0, 0x05      # Enable | INT_PENDING
    SW x12, 8(x11)          # Clear interrupt
    
    # Restore registers
    LW x10, 0(x2)
    LW x11, 4(x2)
    LW x12, 8(x2)
    LW x13, 12(x2)
    LW x14, 16(x2)
    LW x1, 20(x2)
    ADDI x2, x2, 32
    
    # Return from interrupt
    MRET

.data
