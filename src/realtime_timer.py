"""
Real-Time Timer module for the RISC VM
Implements a wall-clock based timer that can generate interrupts at configurable frequencies
"""

import time

class RealTimeTimer:
    """
    Real-time hardware timer with interrupt generation
    - Wall-clock based timing (not instruction-cycle based)
    - Configurable frequency from 1 Hz to 1000 Hz
    - Periodic and one-shot modes
    - Polling-based checking for deterministic behavior
    """
    
    # Control register bit masks
    CTRL_ENABLE = 0x01      # Bit 0: Enable timer
    CTRL_MODE = 0x02        # Bit 1: 0=periodic, 1=one-shot
    CTRL_INT_PENDING = 0x04 # Bit 2: Interrupt pending
    CTRL_ALARM_MODE = 0x08  # Bit 3: Use compare for alarm
    
    def __init__(self):
        """Initialize real-time timer hardware"""
        self.counter = 0
        self.frequency = 1  # Hz (1-1000)
        self.control = 0
        self.compare = 0  # For alarm mode
        self.interrupt_pending = False
        
        # Internal state
        self.last_tick_time = None
        self.start_time = None
        
    def reset(self):
        """Reset timer to initial state"""
        self.counter = 0
        self.frequency = 1
        self.control = 0
        self.compare = 0
        self.interrupt_pending = False
        self.last_tick_time = None
        self.start_time = None
    
    def check(self):
        """
        Check if timer should fire based on wall-clock time
        Called by VM on each instruction step
        
        Returns:
            True if interrupt should be generated
        """
        # Check if timer is enabled
        if not (self.control & self.CTRL_ENABLE):
            return False
        
        current_time = time.perf_counter()
        
        # Initialize timing on first check after enable
        if self.last_tick_time is None:
            self.last_tick_time = current_time
            self.start_time = current_time
            return False
        
        # Calculate period in seconds
        period = 1.0 / max(1, min(1000, self.frequency))
        
        # Check if enough time has elapsed
        elapsed = current_time - self.last_tick_time
        
        if elapsed >= period:
            # Calculate how many ticks occurred (handle slow VM)
            ticks_occurred = int(elapsed / period)
            
            # Increment counter
            self.counter = (self.counter + ticks_occurred) & 0xFFFFFFFF
            
            # Update last tick time (maintain accuracy)
            self.last_tick_time += ticks_occurred * period
            
            # Set interrupt pending
            self.control |= self.CTRL_INT_PENDING
            self.interrupt_pending = True
            
            # Check if we need to stop (one-shot or alarm mode)
            is_one_shot = bool(self.control & self.CTRL_MODE)
            is_alarm_mode = bool(self.control & self.CTRL_ALARM_MODE)
            
            if is_one_shot:
                # One-shot mode: disable timer
                self.control &= ~self.CTRL_ENABLE
            elif is_alarm_mode and self.compare > 0:
                # Alarm mode: check if counter reached compare value
                if self.counter >= self.compare:
                    self.control &= ~self.CTRL_ENABLE
            
            return True
        
        return False
    
    def read_counter(self):
        """Read current counter value"""
        return self.counter
    
    def write_counter(self, value):
        """Write counter value"""
        self.counter = value & 0xFFFFFFFF
    
    def read_frequency(self):
        """Read frequency setting in Hz"""
        return self.frequency
    
    def write_frequency(self, value):
        """Write frequency setting (1-1000 Hz)"""
        self.frequency = max(1, min(1000, value & 0xFFFFFFFF))
    
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
        value_masked = value & ~self.CTRL_INT_PENDING  # Remove pending bit from value
        current_pending = self.control & self.CTRL_INT_PENDING  # Save current pending
        self.control = (value_masked | current_pending) & 0x0F
        
        # If timer is being enabled, reset timing
        if (self.control & self.CTRL_ENABLE) and self.last_tick_time is None:
            self.last_tick_time = time.perf_counter()
            self.start_time = self.last_tick_time
    
    def read_status(self):
        """Read status register"""
        status = 0
        if self.control & self.CTRL_ENABLE:
            status |= 0x01  # Running
        if self.interrupt_pending:
            status |= 0x02  # Interrupt pending
        return status
    
    def read_compare(self):
        """Read compare value"""
        return self.compare
    
    def write_compare(self, value):
        """Write compare value"""
        self.compare = value & 0xFFFFFFFF
    
    def has_pending_interrupt(self):
        """Check if timer has pending interrupt"""
        return self.interrupt_pending
    
    def clear_interrupt(self):
        """Clear pending interrupt"""
        self.control &= ~self.CTRL_INT_PENDING
        self.interrupt_pending = False
    
    def get_elapsed_time(self):
        """Get elapsed time in seconds since timer started"""
        if self.start_time is None:
            return 0.0
        return time.perf_counter() - self.start_time
