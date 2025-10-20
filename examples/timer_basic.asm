# Timer Interrupt Example
# Demonstrates hardware timer interrupts
# Sets up a timer to interrupt every 1000 instructions
# and increments a counter in the interrupt handler

.text
    # Initialize counter at address 0x10000
    LUI x10, 0x10        # x10 = 0x10000 (data segment)
    ADDI x11, x0, 0      # Counter starts at 0
    SW x11, 0(x10)       # Store counter
    
    # Set up interrupt handler address
    # Handler is at label 'interrupt_handler' which will be at PC offset
    LUI x1, 0x0          # Upper 20 bits
    ADDI x1, x1, 68      # handler at instruction 17 = byte 68 (17*4)
    CSRRW x0, 0x305, x1  # Write to mtvec (CSR 0x305)
    
    # Configure timer for 1000 instruction intervals
    LUI x1, 0xF8         # Upper bits
    ADDI x1, x1, -512    # Timer base = 0xF7E00
    ADDI x2, x0, 1000    # Compare value = 1000
    SW x2, 4(x1)         # Write to TIMER_COMPARE (offset 4)
    
    # Set timer control: Enable | Periodic | AutoReload
    ADDI x2, x0, 0x0B    # bits: 1011 = Enable|Periodic|AutoReload
    SW x2, 8(x1)         # Write to TIMER_CONTROL (offset 8)
    
    # Enable timer interrupts in MIE register
    ADDI x2, x0, 0x80    # Timer interrupt enable bit
    CSRRW x0, 0x304, x2  # Write to mie (CSR 0x304)
    
    # Enable global interrupts in mstatus
    ADDI x2, x0, 0x08    # MIE bit in mstatus
    CSRRW x0, 0x300, x2  # Write to mstatus (CSR 0x300)
    
main_loop:
    # Main program loop - just waste time
    LW x11, 0(x10)       # Load counter
    
    # Display counter on screen
    LUI x20, 0xF0        # Display buffer base = 0xF0000
    ADDI x20, x20, 0x000
    
    # Convert counter to ASCII and display (simplified)
    ADDI x21, x11, 48    # Convert to ASCII digit ('0' + value)
    ANDI x21, x21, 0xFF  # Keep only low byte
    SW x21, 0(x20)       # Write to display
    
    # Keep looping
    JAL x0, main_loop    # Jump back to main_loop
    
interrupt_handler:
    # Save context (only registers we'll use)
    ADDI x2, x2, -16     # Adjust stack pointer
    SW x10, 0(x2)        # Save x10
    SW x11, 4(x2)        # Save x11
    SW x12, 8(x2)        # Save x12
    
    # Increment counter
    LUI x10, 0x10        # Counter address
    LW x11, 0(x10)       # Load counter
    ADDI x11, x11, 1     # Increment
    SW x11, 0(x10)       # Store back
    
    # Clear timer interrupt pending bit
    LUI x12, 0xF8        # Upper bits
    ADDI x12, x12, -512  # Timer base = 0xF7E00
    ADDI x11, x0, 0x0F   # All control bits including INT_PENDING
    SW x11, 8(x12)       # Clear interrupt, maintain timer config
    
    # Restore context
    LW x10, 0(x2)
    LW x11, 4(x2)
    LW x12, 8(x2)
    ADDI x2, x2, 16      # Restore stack pointer
    
    # Return from interrupt
    MRET
