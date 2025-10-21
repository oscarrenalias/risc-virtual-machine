"""
Unit tests for RealTimeTimer module  
Tests wall-clock timing, frequency configuration, and interrupt generation
"""

import pytest
import time
from src.realtime_timer import RealTimeTimer


class TestRTTimerBasics:
    """Test basic RT timer initialization"""
    
    def test_rt_timer_initialization(self, rt_timer):
        """Test RT timer initializes with correct defaults"""
        assert rt_timer.counter == 0
        assert rt_timer.frequency == 1
        assert rt_timer.control == 0
        assert rt_timer.interrupt_pending is False
        
    def test_rt_timer_reset(self, rt_timer):
        """Test resetting RT timer"""
        rt_timer.counter = 100
        rt_timer.frequency = 10
        rt_timer.control = 0xFF
        
        rt_timer.reset()
        
        assert rt_timer.counter == 0
        assert rt_timer.frequency == 1
        assert rt_timer.control == 0


class TestRTTimerRegisters:
    """Test RT timer register access"""
    
    def test_read_write_counter(self, rt_timer):
        """Test counter register read/write"""
        rt_timer.write_counter(42)
        assert rt_timer.read_counter() == 42
        
    def test_read_write_frequency(self, rt_timer):
        """Test frequency register read/write"""
        rt_timer.write_frequency(10)
        assert rt_timer.read_frequency() == 10
        
    def test_read_write_control(self, rt_timer):
        """Test control register read/write"""
        rt_timer.write_control(RealTimeTimer.CTRL_ENABLE)
        assert rt_timer.read_control() & RealTimeTimer.CTRL_ENABLE
        
    def test_read_write_compare(self, rt_timer):
        """Test compare register read/write"""
        rt_timer.write_compare(100)
        assert rt_timer.read_compare() == 100
        
    def test_read_status(self, rt_timer):
        """Test status register"""
        status = rt_timer.read_status()
        assert status == 0
        
        rt_timer.control = RealTimeTimer.CTRL_ENABLE
        status = rt_timer.read_status()
        assert status & 0x01


class TestRTTimerTiming:
    """Test RT timer timing behavior"""
    
    @pytest.mark.slow
    def test_timer_ticks_with_wall_clock(self, rt_timer):
        """Test timer uses wall-clock time"""
        rt_timer.write_frequency(10)  # 10 Hz = 100ms period
        rt_timer.write_control(RealTimeTimer.CTRL_ENABLE)
        
        # First check initializes timing
        rt_timer.check()
        
        # Should not fire immediately
        assert rt_timer.check() is False
        
        # Wait for period and check again
        time.sleep(0.11)  # Wait slightly more than 100ms
        result = rt_timer.check()
        
        # Should have fired
        assert result is True
        assert rt_timer.counter == 1
        
    def test_disabled_timer_does_not_fire(self, rt_timer):
        """Test disabled timer doesn't fire"""
        rt_timer.write_frequency(1000)  # 1000 Hz
        rt_timer.write_control(0)  # Disabled
        
        time.sleep(0.002)  # Wait 2ms
        assert rt_timer.check() is False
        assert rt_timer.counter == 0
