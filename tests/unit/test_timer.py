"""
Unit tests for Timer module
Tests counter, compare, prescaler, modes, and control register operations
"""

import pytest
from src.timer import Timer


class TestTimerBasics:
    """Test basic timer initialization and state"""
    
    def test_timer_initialization(self, timer):
        """Test timer initializes with correct defaults"""
        assert timer.counter == 0
        assert timer.compare == 0
        assert timer.control == 0
        assert timer.prescaler == 1
        assert timer.interrupt_pending is False
        
    def test_timer_reset(self, timer):
        """Test resetting timer"""
        timer.counter = 100
        timer.compare = 500
        timer.control = 0xFF
        timer.interrupt_pending = True
        
        timer.reset()
        
        assert timer.counter == 0
        assert timer.compare == 0
        assert timer.control == 0
        assert timer.interrupt_pending is False


class TestTimerTick:
    """Test timer tick behavior"""
    
    def test_tick_disabled_timer_does_nothing(self, timer):
        """Test disabled timer doesn't tick"""
        timer.compare = 10
        assert timer.tick() is False
        assert timer.counter == 0
        
    def test_tick_enabled_timer_increments(self, timer):
        """Test enabled timer increments counter"""
        timer.control = Timer.CTRL_ENABLE
        timer.compare = 100
        
        timer.tick()
        assert timer.counter == 1
        
        timer.tick()
        assert timer.counter == 2
        
    def test_tick_fires_interrupt_on_compare_match(self, timer):
        """Test timer fires interrupt when counter reaches compare"""
        timer.control = Timer.CTRL_ENABLE
        timer.compare = 5
        
        for i in range(4):
            assert timer.tick() is False
        
        # 5th tick should fire interrupt
        assert timer.tick() is True
        assert timer.interrupt_pending is True
        
    def test_prescaler_divides_clock(self, timer):
        """Test prescaler divides timer clock"""
        timer.control = Timer.CTRL_ENABLE
        timer.prescaler = 4
        timer.compare = 100
        
        # Should take 4 ticks to increment counter once
        assert timer.tick() is False
        assert timer.counter == 0
        assert timer.tick() is False
        assert timer.counter == 0
        assert timer.tick() is False
        assert timer.counter == 0
        assert timer.tick() is False
        assert timer.counter == 1


class TestTimerModes:
    """Test timer modes"""
    
    def test_one_shot_mode_disables_after_fire(self, timer):
        """Test one-shot mode disables timer after interrupt"""
        timer.control = Timer.CTRL_ENABLE  # One-shot (MODE bit = 0)
        timer.compare = 3
        
        # Tick 3 times: counter goes from 0->1, 1->2, 2->3
        for i in range(3):
            result = timer.tick()
            # Should not fire until counter >= compare
            if i < 2:
                assert result is False
        
        # After 3 ticks, counter is 3 and should have fired
        assert timer.counter == 3
        assert timer.interrupt_pending is True
        # One-shot mode should disable timer
        assert (timer.control & Timer.CTRL_ENABLE) == 0
        
    def test_periodic_mode_auto_reload(self, timer):
        """Test periodic mode with auto-reload"""
        timer.control = Timer.CTRL_ENABLE | Timer.CTRL_MODE | Timer.CTRL_AUTO_RELOAD
        timer.compare = 3
        
        # Tick 3 times: counter goes 0->1, 1->2, 2->3 and fires
        result1 = timer.tick()
        assert result1 is False
        result2 = timer.tick()
        assert result2 is False
        result3 = timer.tick()
        # On 3rd tick, counter reaches 3, fires and reloads
        assert result3 is True
        assert timer.counter == 0  # Reloaded
        assert (timer.control & Timer.CTRL_ENABLE) != 0  # Still enabled


class TestTimerRegisters:
    """Test timer register access"""
    
    def test_read_write_counter(self, timer):
        """Test counter register read/write"""
        timer.write_counter(42)
        assert timer.read_counter() == 42
        
    def test_read_write_compare(self, timer):
        """Test compare register read/write"""
        timer.write_compare(1000)
        assert timer.read_compare() == 1000
        
    def test_read_write_control(self, timer):
        """Test control register read/write"""
        timer.write_control(Timer.CTRL_ENABLE | Timer.CTRL_MODE)
        assert timer.read_control() & Timer.CTRL_ENABLE
        assert timer.read_control() & Timer.CTRL_MODE
        
    def test_write_control_clears_interrupt_pending(self, timer):
        """Test writing pending bit clears interrupt"""
        timer.control = Timer.CTRL_INT_PENDING
        timer.interrupt_pending = True
        
        timer.write_control(Timer.CTRL_INT_PENDING | Timer.CTRL_ENABLE)
        
        assert timer.interrupt_pending is False
        assert (timer.control & Timer.CTRL_INT_PENDING) == 0
        
    def test_read_write_prescaler(self, timer):
        """Test prescaler register read/write"""
        timer.write_prescaler(8)
        assert timer.read_prescaler() == 8
        
    def test_prescaler_minimum_one(self, timer):
        """Test prescaler cannot be less than 1"""
        timer.write_prescaler(0)
        assert timer.read_prescaler() == 1
        
    def test_read_status(self, timer):
        """Test status register reflects timer state"""
        status = timer.read_status()
        assert status == 0  # Not running, no interrupt
        
        timer.control = Timer.CTRL_ENABLE
        status = timer.read_status()
        assert status & 0x01  # Running
        
        timer.interrupt_pending = True
        status = timer.read_status()
        assert status & 0x02  # Interrupt pending


class TestTimerInterrupts:
    """Test timer interrupt handling"""
    
    def test_has_pending_interrupt(self, timer):
        """Test checking for pending interrupt"""
        assert timer.has_pending_interrupt() is False
        
        timer.interrupt_pending = True
        assert timer.has_pending_interrupt() is True
        
    def test_clear_interrupt(self, timer):
        """Test clearing pending interrupt"""
        timer.interrupt_pending = True
        timer.control = Timer.CTRL_INT_PENDING
        
        timer.clear_interrupt()
        
        assert timer.interrupt_pending is False
        assert (timer.control & Timer.CTRL_INT_PENDING) == 0
