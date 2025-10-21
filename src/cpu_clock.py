"""
CPU Clock module for the RISC VM
Simulates a CPU clock running at a configurable frequency
"""

import time
import logging

logger = logging.getLogger(__name__)


class CPUClock:
    """
    CPU clock that controls instruction execution speed
    
    Simulates a real CPU clock by enforcing timing between instruction cycles.
    The clock can be disabled for maximum-speed execution.
    """
    
    MIN_FREQUENCY = 1      # 1 Hz
    MAX_FREQUENCY = 10000  # 10 kHz
    
    def __init__(self, frequency_hz=1000, enabled=True):
        """
        Initialize CPU clock
        
        Args:
            frequency_hz: Clock frequency in Hz (1-10000). Default: 1000 Hz (1 kHz)
            enabled: If False, clock runs at maximum speed (no delays)
        """
        self.enabled = enabled
        self._frequency = self._validate_frequency(frequency_hz)
        self._cycle_time = 1.0 / self._frequency if self.enabled else 0.0
        self._last_tick = None
        self._cycle_count = 0
        
    def _validate_frequency(self, freq):
        """Validate and clamp frequency to valid range"""
        if freq < self.MIN_FREQUENCY:
            logger.warning(f"Frequency {freq} Hz too low, clamping to {self.MIN_FREQUENCY} Hz")
            return self.MIN_FREQUENCY
        if freq > self.MAX_FREQUENCY:
            logger.warning(f"Frequency {freq} Hz too high, clamping to {self.MAX_FREQUENCY} Hz")
            return self.MAX_FREQUENCY
        return freq
    
    @property
    def frequency(self):
        """Get current clock frequency in Hz"""
        return self._frequency
    
    @frequency.setter
    def frequency(self, freq_hz):
        """Set clock frequency in Hz"""
        self._frequency = self._validate_frequency(freq_hz)
        self._cycle_time = 1.0 / self._frequency if self.enabled else 0.0
        logger.info(f"Clock frequency set to {self._frequency} Hz (period: {self._cycle_time*1000:.3f} ms)")
    
    def enable(self):
        """Enable the clock (enforce timing)"""
        self.enabled = True
        self._cycle_time = 1.0 / self._frequency
        self._last_tick = None  # Reset timing
        logger.info(f"Clock enabled at {self._frequency} Hz")
    
    def disable(self):
        """Disable the clock (maximum speed execution)"""
        self.enabled = False
        self._cycle_time = 0.0
        self._last_tick = None
        logger.info("Clock disabled - running at maximum speed")
    
    def tick(self):
        """
        Tick the clock - enforce one cycle time delay
        
        This method should be called once per instruction cycle.
        It will sleep for the appropriate amount of time to maintain
        the configured frequency.
        """
        if not self.enabled:
            # Clock disabled, run at max speed
            self._cycle_count += 1
            return
        
        current_time = time.perf_counter()
        
        # Initialize on first tick
        if self._last_tick is None:
            self._last_tick = current_time
            self._cycle_count += 1
            return
        
        # Calculate how long to sleep to maintain frequency
        elapsed = current_time - self._last_tick
        sleep_time = self._cycle_time - elapsed
        
        if sleep_time > 0:
            # Sleep for the remaining cycle time
            # Note: time.sleep() is not perfectly accurate, but good enough
            # for educational/visualization purposes
            time.sleep(sleep_time)
            self._last_tick += self._cycle_time
        else:
            # We're running behind - just update last_tick and continue
            # This can happen at high frequencies or under system load
            self._last_tick = current_time
        
        self._cycle_count += 1
    
    def reset(self):
        """Reset the clock state"""
        self._last_tick = None
        self._cycle_count = 0
    
    def get_cycle_count(self):
        """Get the number of cycles that have elapsed"""
        return self._cycle_count
    
    def get_actual_frequency(self):
        """
        Get the actual measured frequency based on elapsed time
        
        Returns:
            Actual frequency in Hz, or None if not enough data
        """
        if not self.enabled or self._cycle_count < 2 or self._last_tick is None:
            return None
        
        current_time = time.perf_counter()
        # Calculate from first tick to now
        if self._cycle_count > 0:
            # Rough estimate
            return self._cycle_count / (current_time - self._last_tick + self._cycle_time * self._cycle_count)
        
        return None
    
    def __str__(self):
        """String representation"""
        if not self.enabled:
            return "CPUClock(disabled - max speed)"
        return f"CPUClock({self._frequency} Hz, {self._cycle_time*1000:.3f} ms/cycle)"
    
    def __repr__(self):
        """Detailed representation"""
        return f"CPUClock(frequency={self._frequency}, enabled={self.enabled}, cycles={self._cycle_count})"
