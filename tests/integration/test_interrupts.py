"""
Integration tests for interrupts and timers
Tests interrupt handling through full VM execution
"""

import pytest
from tests.fixtures.test_helpers import run_program_until_halt, assert_register_equals


class TestTimerInterrupts:
    """Test timer interrupt integration with CPU"""
    
    def test_basic_timer_interrupt(self, vm):
        """Test timer fires interrupt and handler executes"""
        program = """
        # Initialize counter
        ADDI x10, x0, 0      # x10 = interrupt count
        
        # Set interrupt handler address
        ADDI x1, x0, handler
        CSRRW x0, 0x305, x1  # mtvec = handler address
        
        # Configure timer for 10 instruction intervals
        LUI x1, 0xF8
        ADDI x1, x1, -512    # Timer base = 0xF7E00
        ADDI x2, x0, 10      # Compare = 10
        SW x2, 4(x1)         # TIMER_COMPARE
        
        ADDI x2, x0, 0x0B    # Enable|Periodic|AutoReload
        SW x2, 8(x1)         # TIMER_CONTROL
        
        # Enable timer interrupt
        ADDI x2, x0, 0x80
        CSRRW x0, 0x304, x2  # mie = timer interrupt enable
        
        # Enable global interrupts
        ADDI x2, x0, 0x08
        CSRRW x0, 0x300, x2  # mstatus.MIE = 1
        
    loop:
        # Check if we've had an interrupt
        ADDI x11, x0, 1
        BGE x10, x11, done
        JAL x0, loop
        
    done:
        HALT
    
    handler:
        # Increment counter
        ADDI x10, x10, 1
        
        # Clear interrupt pending
        LUI x1, 0xF8
        ADDI x1, x1, -512
        ADDI x2, x0, 0x0F
        SW x2, 8(x1)
        
        MRET
        """
        
        count = run_program_until_halt(vm, program, max_instructions=1000)
        
        # Should have received at least 1 interrupt
        interrupt_count = vm.cpu.read_register(10)
        assert interrupt_count >= 1
        assert count < 1000  # Should complete well before limit


class TestWFIWithInterrupts:
    """Test WFI (Wait For Interrupt) functionality"""
    
    def test_wfi_waits_for_timer(self, vm):
        """Test WFI waits until timer interrupt occurs"""
        program = """
        # Initialize
        ADDI x20, x0, 0      # Interrupt counter
        
        # Set handler
        ADDI x1, x0, handler
        CSRRW x0, 0x305, x1
        
        # Configure timer for 50 cycles
        LUI x1, 0xF8
        ADDI x1, x1, -512
        ADDI x2, x0, 50
        SW x2, 4(x1)         # Compare = 50
        ADDI x2, x0, 0x0B
        SW x2, 8(x1)         # Enable timer
        
        # Enable interrupts
        ADDI x2, x0, 0x80
        CSRRW x0, 0x304, x2
        ADDI x2, x0, 0x08
        CSRRW x0, 0x300, x2
        
        # Wait for interrupt
        WFI
        
        # After WFI, should have received interrupt
        HALT
        
    handler:
        ADDI x20, x20, 1
        
        # Clear pending
        LUI x1, 0xF8
        ADDI x1, x1, -512
        ADDI x2, x0, 0x0F
        SW x2, 8(x1)
        
        MRET
        """
        
        run_program_until_halt(vm, program, max_instructions=5000)
        
        # Should have received interrupt
        interrupt_count = vm.cpu.read_register(20)
        assert interrupt_count == 1


class TestCSROperations:
    """Test CSR instruction integration"""
    
    def test_csrrw_read_write(self, vm):
        """Test CSRRW (atomic read/write)"""
        program = """
        # Write value to CSR
        ADDI x1, x0, 0x12
        CSRRW x2, 0x305, x1  # Write x1 to mtvec, read old value to x2
        
        # Read back
        CSRRW x3, 0x305, x0  # Read mtvec to x3 (writing 0)
        
        HALT
        """
        
        run_program_until_halt(vm, program)
        
        # x2 should have old value (0)
        assert vm.cpu.read_register(2) == 0
        # x3 should have value we wrote (0x12)
        assert vm.cpu.read_register(3) == 0x12
        
    def test_csrrs_set_bits(self, vm):
        """Test CSRRS (set bits)"""
        program = """
        # Initial write
        ADDI x1, x0, 0x0F
        CSRRW x0, 0x305, x1  # mtvec = 0x0F
        
        # Set additional bits
        ADDI x2, x0, 0xF0
        CSRRS x3, 0x305, x2  # Set bits, read old to x3
        
        # Read final value
        CSRRS x4, 0x305, x0  # Read without changing
        
        HALT
        """
        
        run_program_until_halt(vm, program)
        
        # x3 should have old value
        assert vm.cpu.read_register(3) == 0x0F
        # x4 should have combined value
        assert vm.cpu.read_register(4) == 0xFF
        
    def test_csrrc_clear_bits(self, vm):
        """Test CSRRC (clear bits)"""
        program = """
        # Set initial value
        ADDI x1, x0, 0xFF
        CSRRW x0, 0x305, x1  # mtvec = 0xFF
        
        # Clear some bits
        ADDI x2, x0, 0x0F
        CSRRC x3, 0x305, x2  # Clear bits, read old to x3
        
        # Read final value
        CSRRS x4, 0x305, x0
        
        HALT
        """
        
        run_program_until_halt(vm, program)
        
        # x3 should have old value
        assert vm.cpu.read_register(3) == 0xFF
        # x4 should have cleared value
        assert vm.cpu.read_register(4) == 0xF0


class TestInterruptPriority:
    """Test interrupt priority handling"""
    
    @pytest.mark.slow
    def test_multiple_interrupt_sources(self, vm):
        """Test handling interrupts from both timers"""
        program = """
        ADDI x10, x0, 0      # Cycle timer count
        ADDI x11, x0, 0      # RT timer count
        
        # Set handler
        ADDI x1, x0, handler
        CSRRW x0, 0x305, x1
        
        # Configure cycle timer
        LUI x1, 0xF8
        ADDI x1, x1, -512
        ADDI x2, x0, 30
        SW x2, 4(x1)
        ADDI x2, x0, 0x0B
        SW x2, 8(x1)
        
        # Configure RT timer (10 Hz = 100ms period)
        ADDI x2, x0, 10
        SW x2, 36(x1)        # RT_TIMER_FREQUENCY
        ADDI x2, x0, 0x01
        SW x2, 40(x1)        # RT_TIMER_CONTROL (enable)
        
        # Enable both interrupt sources
        ADDI x2, x0, 0x880   # Both timer bits
        CSRRW x0, 0x304, x2
        
        # Enable global interrupts
        ADDI x2, x0, 0x08
        CSRRW x0, 0x300, x2
        
    loop:
        # Run for a bit
        ADDI x12, x0, 2
        BGE x10, x12, done
        JAL x0, loop
        
    done:
        HALT
        
    handler:
        # Check which interrupt
        CSRRS x15, 0x342, x0  # Read mcause
        
        # Check if cycle timer (0x80000007)
        LUI x16, 0x80000
        ADDI x16, x16, 7
        BEQ x15, x16, cycle_handler
        
        # Otherwise RT timer
        ADDI x11, x11, 1
        JAL x0, clear_int
        
    cycle_handler:
        ADDI x10, x10, 1
        
    clear_int:
        # Clear timer pending
        LUI x1, 0xF8
        ADDI x1, x1, -512
        ADDI x2, x0, 0x0F
        SW x2, 8(x1)
        
        MRET
        """
        
        run_program_until_halt(vm, program, max_instructions=5000)
        
        # Should have received cycle timer interrupts
        cycle_count = vm.cpu.read_register(10)
        assert cycle_count >= 2
