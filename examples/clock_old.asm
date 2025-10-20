# Digital Clock - Never-ending clock display
# Displays time in HH:MM:SS format in the center of the screen
# Updates every "second" (simulated with delay loop)

.text
main:
    # Initialize time to 00:00:00
    ADDI x20, x0, 0         # x20 = hours
    ADDI x21, x0, 0         # x21 = minutes
    ADDI x22, x0, 0         # x22 = seconds
    
    # Load display base address
    LUI x10, 0xF0           # x10 = 0xF0000 (display buffer base)

clock_loop:
    # Clear the clock line (row 12, centered)
    # Position: row 12 * 80 * 4 = 3840 = 0xF00 + base
    ADDI x11, x10, 3840     # x11 = position for row 12
    
    # Add offset to center (column 35 for "HH:MM:SS" = 8 chars)
    ADDI x11, x11, 560      # x11 += 35*4*4 = 560 (center position)
    
    # Display hours (tens digit)
    ADDI x12, x20, 0        # Copy hours
    ADDI x13, x0, 10        # Divisor
    
    # Get tens digit of hours
    ADDI x14, x0, 0         # Counter for division
div_hours_tens:
    BLT x12, x13, done_hours_tens
    SUB x12, x12, x13
    ADDI x14, x14, 1
    JAL x0, div_hours_tens
done_hours_tens:
    ADDI x14, x14, 48       # Convert to ASCII ('0' = 48)
    SW x14, 0(x11)          # Write tens digit
    
    # Display hours (ones digit)
    ADDI x12, x12, 48       # Convert remainder to ASCII
    SW x12, 4(x11)          # Write ones digit
    
    # Display colon
    ADDI x14, x0, 58        # ':' = 58
    SW x14, 8(x11)
    
    # Display minutes (tens digit)
    ADDI x12, x21, 0        # Copy minutes
    ADDI x14, x0, 0         # Counter
div_min_tens:
    BLT x12, x13, done_min_tens
    SUB x12, x12, x13
    ADDI x14, x14, 1
    JAL x0, div_min_tens
done_min_tens:
    ADDI x14, x14, 48       # Convert to ASCII
    SW x14, 12(x11)         # Write tens digit
    
    # Display minutes (ones digit)
    ADDI x12, x12, 48       # Convert remainder to ASCII
    SW x12, 16(x11)         # Write ones digit
    
    # Display colon
    ADDI x14, x0, 58        # ':' = 58
    SW x14, 20(x11)
    
    # Display seconds (tens digit)
    ADDI x12, x22, 0        # Copy seconds
    ADDI x14, x0, 0         # Counter
div_sec_tens:
    BLT x12, x13, done_sec_tens
    SUB x12, x12, x13
    ADDI x14, x14, 1
    JAL x0, div_sec_tens
done_sec_tens:
    ADDI x14, x14, 48       # Convert to ASCII
    SW x14, 24(x11)         # Write tens digit
    
    # Display seconds (ones digit)
    ADDI x12, x12, 48       # Convert remainder to ASCII
    SW x12, 28(x11)         # Write ones digit
    
    # Add a title above the clock
    ADDI x11, x10, 3520     # Row 11 * 80 * 4 = 3520
    ADDI x11, x11, 544      # Center "DIGITAL CLOCK"
    
    ADDI x14, x0, 68        # 'D'
    SW x14, 0(x11)
    ADDI x14, x0, 73        # 'I'
    SW x14, 4(x11)
    ADDI x14, x0, 71        # 'G'
    SW x14, 8(x11)
    ADDI x14, x0, 73        # 'I'
    SW x14, 12(x11)
    ADDI x14, x0, 84        # 'T'
    SW x14, 16(x11)
    ADDI x14, x0, 65        # 'A'
    SW x14, 20(x11)
    ADDI x14, x0, 76        # 'L'
    SW x14, 24(x11)
    ADDI x14, x0, 32        # ' '
    SW x14, 28(x11)
    ADDI x14, x0, 67        # 'C'
    SW x14, 32(x11)
    ADDI x14, x0, 76        # 'L'
    SW x14, 36(x11)
    ADDI x14, x0, 79        # 'O'
    SW x14, 40(x11)
    ADDI x14, x0, 67        # 'C'
    SW x14, 44(x11)
    ADDI x14, x0, 75        # 'K'
    SW x14, 48(x11)
    
    # Delay loop (smaller delay to see updates before instruction limit)
    ADDI x15, x0, 100       # Small delay counter
delay_loop:
    ADDI x15, x15, -1
    BNE x15, x0, delay_loop
    
    # Increment seconds
    ADDI x22, x22, 1
    ADDI x13, x0, 60
    BLT x22, x13, clock_loop
    
    # Seconds overflow: reset to 0, increment minutes
    ADDI x22, x0, 0
    ADDI x21, x21, 1
    BLT x21, x13, clock_loop
    
    # Minutes overflow: reset to 0, increment hours
    ADDI x21, x0, 0
    ADDI x20, x20, 1
    ADDI x13, x0, 24
    BLT x20, x13, clock_loop
    
    # Hours overflow: reset to 0
    ADDI x20, x0, 0
    JAL x0, clock_loop      # Continue forever

.data
