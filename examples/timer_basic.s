# Timer Interrupt Example
# Demonstrates hardware timer interrupts
# Sets up a timer to interrupt every 1000 instructions
# and increments a counter in the interrupt handler
# Uses RISC-V ABI register names and character literals

.text
main:
    # Initialize counter at address 0x10000
    LUI s0, 0x10            # s0 = 0x10000 (data segment)
    ADDI s1, zero, 0        # Counter starts at 0
    SW s1, 0(s0)            # Store counter
    
    # Set up interrupt handler address using label
    LUI ra, 0x0             # Upper 20 bits
    ADDI ra, ra, interrupt_handler  # Handler address from label
    CSRRW zero, 0x305, ra   # Write to mtvec (CSR 0x305)
    
    # Configure timer for 1000 instruction intervals
    LUI a0, 0xF8            # Upper bits
    ADDI a0, a0, -512       # Timer base = 0xF7E00
    ADDI a1, zero, 1000     # Compare value = 1000
    SW a1, 4(a0)            # Write to TIMER_COMPARE (offset 4)
    
    # Set timer control: Enable | Periodic | AutoReload
    ADDI a1, zero, 0x0B     # bits: 1011 = Enable|Periodic|AutoReload
    SW a1, 8(a0)            # Write to TIMER_CONTROL (offset 8)
    
    # Enable timer interrupts in MIE register
    ADDI a1, zero, 0x80     # Timer interrupt enable bit
    CSRRW zero, 0x304, a1   # Write to mie (CSR 0x304)
    
    # Enable global interrupts in mstatus
    ADDI a1, zero, 0x08     # MIE bit in mstatus
    CSRRW zero, 0x300, a1   # Write to mstatus (CSR 0x300)
    
main_loop:
    # Main program loop - just waste time
    LW s1, 0(s0)            # Load counter
    
    # Display counter on screen
    LUI t0, 0xF0            # Display buffer base = 0xF0000
    ADDI t0, t0, 0x000
    
    # Convert counter to ASCII and display (simplified)
    ADDI t1, s1, '0'        # Convert to ASCII digit ('0' + value)
    ANDI t1, t1, 0xFF       # Keep only low byte
    SW t1, 0(t0)            # Write to display
    
    # Keep looping
    JAL zero, main_loop     # Jump back to main_loop
    
interrupt_handler:
    # Save context (only registers we'll use)
    ADDI sp, sp, -16        # Adjust stack pointer
    SW a0, 0(sp)            # Save a0
    SW a1, 4(sp)            # Save a1
    SW a2, 8(sp)            # Save a2
    
    # Increment counter
    LUI a0, 0x10            # Counter address
    LW a1, 0(a0)            # Load counter
    ADDI a1, a1, 1          # Increment
    SW a1, 0(a0)            # Store back
    
    # Clear timer interrupt pending bit
    LUI a2, 0xF8            # Upper bits
    ADDI a2, a2, -512       # Timer base = 0xF7E00
    ADDI a1, zero, 0x0F     # All control bits including INT_PENDING
    SW a1, 8(a2)            # Clear interrupt, maintain timer config
    
    # Restore context
    LW a0, 0(sp)
    LW a1, 4(sp)
    LW a2, 8(sp)
    ADDI sp, sp, 16         # Restore stack pointer
    
    # Return from interrupt
    MRET
