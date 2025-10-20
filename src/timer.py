"""
Timer module for the RISC VM
Implements a programmable hardware timer that can generate interrupts
"""

class Timer:
    """
    Hardware timer with interrupt generation
    - 32-bit counter
    - 32-bit compare register
    - Configurable modes (one-shot, periodic)
    - Prescaler for clock division
    """
    
    # Control register bit masks
    CTRL_ENABLE = 0x01      # Bit 0: Enable timer
    CTRL_MODE = 0x02        # Bit 1: 0=one-shot, 1=periodic
    CTRL_INT_PENDING = 0x04 # Bit 2: Interrupt pending
    CTRL_AUTO_RELOAD = 0x08 # Bit 3: Auto-reload counter
    
    def __init__(self):
        """Initialize timer hardware"""
        self.counter = 0
        self.compare = 0
        self.control = 0
        self.prescaler = 1  # Divider for instruction clock
        self.prescaler_counter = 0
        self.interrupt_pending = False
    
    def reset(self):
        """Reset timer to initial state"""
        self.counter = 0
        self.compare = 0
        self.control = 0
        self.prescaler = 1
        self.prescaler_counter = 0
        self.interrupt_pending = False
    
    def tick(self):
        """
        Tick the timer (called once per instruction cycle)
        Returns True if interrupt should be generated
        """
        # Check if timer is enabled
        if not (self.control & self.CTRL_ENABLE):
            return False
        
        # Handle prescaler
        self.prescaler_counter += 1
        if self.prescaler_counter < self.prescaler:
            return False
        
        self.prescaler_counter = 0
        
        # Increment counter
        self.counter = (self.counter + 1) & 0xFFFFFFFF
        
        # Check for compare match
        if self.counter >= self.compare and self.compare > 0:
            # Set interrupt pending
            self.control |= self.CTRL_INT_PENDING
            self.interrupt_pending = True
            
            # Handle mode
            is_periodic = bool(self.control & self.CTRL_MODE)
            auto_reload = bool(self.control & self.CTRL_AUTO_RELOAD)
            
            if is_periodic and auto_reload:
                # Reset counter for next period
                self.counter = 0
            elif not is_periodic:
                # One-shot mode: disable timer
                self.control &= ~self.CTRL_ENABLE
            
            return True
        
        return False
    
    def read_counter(self):
        """Read current counter value"""
        return self.counter
    
    def write_counter(self, value):
        """Write counter value"""
        self.counter = value & 0xFFFFFFFF
    
    def read_compare(self):
        """Read compare value"""
        return self.compare
    
    def write_compare(self, value):
        """Write compare value"""
        self.compare = value & 0xFFFFFFFF
    
    def read_control(self):
        """Read control register"""
        return self.control
    
    def write_control(self, value):
        """Write control register"""
        # Clear interrupt pending if bit 2 is written as 1 (write-1-to-clear)
        if value & self.CTRL_INT_PENDING:
            self.control &= ~self.CTRL_INT_PENDING
            self.interrupt_pending = False
        
        # Update other control bits (but don't touch pending bit unless clearing)
        # Preserve current pending bit, update other bits from value
        value_masked = value & ~self.CTRL_INT_PENDING  # Remove pending bit from value
        current_pending = self.control & self.CTRL_INT_PENDING  # Save current pending
        self.control = (value_masked | current_pending) & 0x0F
    
    def read_prescaler(self):
        """Read prescaler value"""
        return self.prescaler
    
    def write_prescaler(self, value):
        """Write prescaler value"""
        self.prescaler = max(1, value & 0xFFFFFFFF)  # Minimum 1
    
    def read_status(self):
        """Read status register"""
        status = 0
        if self.control & self.CTRL_ENABLE:
            status |= 0x01  # Running
        if self.interrupt_pending:
            status |= 0x02  # Interrupt pending
        return status
    
    def has_pending_interrupt(self):
        """Check if timer has pending interrupt"""
        return self.interrupt_pending
    
    def clear_interrupt(self):
        """Clear pending interrupt"""
        self.control &= ~self.CTRL_INT_PENDING
        self.interrupt_pending = False
