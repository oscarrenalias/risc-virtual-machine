"""
Unit tests for CPU module
Tests register operations, PC management, CSR handling, interrupts, and utilities
"""

import pytest
from src.cpu import CPU


class TestCPUBasics:
    """Test basic CPU initialization and state"""
    
    def test_cpu_initialization(self, cpu):
        """Test CPU initializes with correct defaults"""
        assert cpu.NUM_REGISTERS == 32
        assert cpu.pc == 0
        assert cpu.halted is False
        assert cpu.waiting_for_interrupt is False
        assert cpu.instruction_count == 0
        assert cpu.interrupt_enabled is False
        
    def test_all_registers_initialized_to_zero(self, cpu):
        """Test all registers start at zero"""
        for i in range(cpu.NUM_REGISTERS):
            assert cpu.read_register(i) == 0
            
    def test_csr_initialized(self, cpu):
        """Test CSR registers are initialized"""
        assert cpu.read_csr(cpu.CSR_MSTATUS) == 0
        assert cpu.read_csr(cpu.CSR_MIE) == 0
        assert cpu.read_csr(cpu.CSR_MTVEC) == 0
        assert cpu.read_csr(cpu.CSR_MEPC) == 0
        assert cpu.read_csr(cpu.CSR_MCAUSE) == 0
        assert cpu.read_csr(cpu.CSR_MIP) == 0


class TestRegisterOperations:
    """Test register read/write operations"""
    
    def test_write_and_read_register_by_number(self, cpu):
        """Test writing and reading registers by number"""
        cpu.write_register(5, 0x12345678)
        assert cpu.read_register(5) == 0x12345678
        
    def test_write_and_read_register_by_name(self, cpu):
        """Test writing and reading registers by name"""
        cpu.write_register('x10', 0xDEADBEEF)
        assert cpu.read_register('x10') == 0xDEADBEEF
        
    def test_x0_hardwired_to_zero(self, cpu):
        """Test that x0 always returns 0 and cannot be written"""
        cpu.write_register(0, 0xFFFFFFFF)
        assert cpu.read_register(0) == 0
        
        cpu.write_register('x0', 0x12345678)
        assert cpu.read_register('x0') == 0
        
    def test_register_value_masked_to_32_bits(self, cpu):
        """Test that register values are masked to 32 bits"""
        cpu.write_register(5, 0x1FFFFFFFF)  # 33 bits
        assert cpu.read_register(5) == 0xFFFFFFFF
        
    def test_register_aliases(self, cpu):
        """Test register name aliases work correctly"""
        # Test common aliases
        cpu.write_register('zero', 0x123)
        assert cpu.read_register(0) == 0  # zero is hardwired
        
        cpu.write_register('ra', 0x1000)
        assert cpu.read_register(1) == 0x1000
        
        cpu.write_register('sp', 0x2000)
        assert cpu.read_register(2) == 0x2000
        
        cpu.write_register('gp', 0x3000)
        assert cpu.read_register(3) == 0x3000
        
        cpu.write_register('tp', 0x4000)
        assert cpu.read_register(4) == 0x4000
        
        cpu.write_register('fp', 0x8000)
        assert cpu.read_register(8) == 0x8000
        
        cpu.write_register('s0', 0x8888)
        assert cpu.read_register(8) == 0x8888  # fp and s0 are same
        
    def test_case_insensitive_register_names(self, cpu):
        """Test register names are case-insensitive"""
        cpu.write_register('X10', 0x100)
        assert cpu.read_register('x10') == 0x100
        assert cpu.read_register('X10') == 0x100
        
    def test_invalid_register_number_raises_error(self, cpu):
        """Test invalid register numbers raise ValueError"""
        with pytest.raises(ValueError):
            cpu.read_register(32)
        
        with pytest.raises(ValueError):
            cpu.write_register(-1, 100)
            
        with pytest.raises(ValueError):
            cpu.write_register(100, 100)
            
    def test_invalid_register_name_raises_error(self, cpu):
        """Test invalid register names raise ValueError"""
        with pytest.raises(ValueError):
            cpu.read_register('invalid')
        
        with pytest.raises(ValueError):
            cpu.write_register('x32', 100)
    
    def test_temporary_register_aliases(self, cpu):
        """Test all temporary register ABI names (t0-t6)"""
        # t0-t2 map to x5-x7
        cpu.write_register('t0', 0x1111)
        assert cpu.read_register(5) == 0x1111
        assert cpu.read_register('x5') == 0x1111
        
        cpu.write_register('t1', 0x2222)
        assert cpu.read_register(6) == 0x2222
        
        cpu.write_register('t2', 0x3333)
        assert cpu.read_register(7) == 0x3333
        
        # t3-t6 map to x28-x31
        cpu.write_register('t3', 0x4444)
        assert cpu.read_register(28) == 0x4444
        
        cpu.write_register('t4', 0x5555)
        assert cpu.read_register(29) == 0x5555
        
        cpu.write_register('t5', 0x6666)
        assert cpu.read_register(30) == 0x6666
        
        cpu.write_register('t6', 0x7777)
        assert cpu.read_register(31) == 0x7777
    
    def test_saved_register_aliases(self, cpu):
        """Test all saved register ABI names (s0-s11)"""
        # s0 is x8 (also fp)
        cpu.write_register('s0', 0x1000)
        assert cpu.read_register(8) == 0x1000
        
        # s1 is x9
        cpu.write_register('s1', 0x2000)
        assert cpu.read_register(9) == 0x2000
        
        # s2-s11 map to x18-x27
        for i in range(2, 12):
            value = 0x3000 + i * 0x100
            cpu.write_register(f's{i}', value)
            assert cpu.read_register(18 + i - 2) == value
    
    def test_argument_register_aliases(self, cpu):
        """Test all argument register ABI names (a0-a7)"""
        # a0-a7 map to x10-x17
        for i in range(8):
            value = 0xA000 + i * 0x100
            cpu.write_register(f'a{i}', value)
            assert cpu.read_register(10 + i) == value
            assert cpu.read_register(f'x{10 + i}') == value
    
    def test_mixed_register_notation(self, cpu):
        """Test using both x-notation and ABI names interchangeably"""
        # Write with ABI name, read with x-notation
        cpu.write_register('a0', 0xAAAA)
        assert cpu.read_register('x10') == 0xAAAA
        assert cpu.read_register(10) == 0xAAAA
        
        # Write with x-notation, read with ABI name
        cpu.write_register('x5', 0xBBBB)
        assert cpu.read_register('t0') == 0xBBBB
        
        # Write with number, read with both
        cpu.write_register(2, 0xCCCC)
        assert cpu.read_register('sp') == 0xCCCC
        assert cpu.read_register('x2') == 0xCCCC
    
    def test_case_insensitive_abi_names(self, cpu):
        """Test ABI register names are case-insensitive"""
        cpu.write_register('A0', 0x1111)
        assert cpu.read_register('a0') == 0x1111
        
        cpu.write_register('T0', 0x2222)
        assert cpu.read_register('t0') == 0x2222
        
        cpu.write_register('S1', 0x3333)
        assert cpu.read_register('s1') == 0x3333
        
        cpu.write_register('RA', 0x4444)
        assert cpu.read_register('ra') == 0x4444


class TestProgramCounter:
    """Test program counter operations"""
    
    def test_pc_starts_at_zero(self, cpu):
        """Test PC initializes to 0"""
        assert cpu.pc == 0
        
    def test_increment_pc_default(self, cpu):
        """Test PC increment by default amount (4)"""
        cpu.increment_pc()
        assert cpu.pc == 4
        
        cpu.increment_pc()
        assert cpu.pc == 8
        
    def test_increment_pc_custom_amount(self, cpu):
        """Test PC increment by custom amount"""
        cpu.increment_pc(8)
        assert cpu.pc == 8
        
        cpu.increment_pc(2)
        assert cpu.pc == 10
        
    def test_set_pc(self, cpu):
        """Test setting PC to specific address"""
        cpu.set_pc(0x1000)
        assert cpu.pc == 0x1000
        
        cpu.set_pc(0xDEADBEEF)
        assert cpu.pc == 0xDEADBEEF
        
    def test_set_pc_masked_to_32_bits(self, cpu):
        """Test PC is masked to 32 bits"""
        cpu.set_pc(0x1FFFFFFFF)
        assert cpu.pc == 0xFFFFFFFF


class TestCPUState:
    """Test CPU state operations (halt, reset, etc.)"""
    
    def test_halt(self, cpu):
        """Test halting the CPU"""
        assert cpu.halted is False
        cpu.halt()
        assert cpu.halted is True
        
    def test_reset(self, cpu):
        """Test resetting the CPU"""
        # Modify CPU state
        cpu.write_register(5, 0x12345678)
        cpu.pc = 0x1000
        cpu.halt()
        cpu.instruction_count = 100
        cpu.waiting_for_interrupt = True
        cpu.write_csr(cpu.CSR_MSTATUS, 0xFF)
        
        # Reset
        cpu.reset()
        
        # Check everything is back to initial state
        assert cpu.read_register(5) == 0
        assert cpu.pc == 0
        assert cpu.halted is False
        assert cpu.instruction_count == 0
        assert cpu.waiting_for_interrupt is False
        assert cpu.read_csr(cpu.CSR_MSTATUS) == 0
        assert cpu.interrupt_enabled is False


class TestSignExtension:
    """Test sign extension utilities"""
    
    def test_sign_extend_positive_8_bit(self, cpu):
        """Test sign extending positive 8-bit values"""
        assert cpu.sign_extend(0x7F, 8) == 0x7F
        assert cpu.sign_extend(0x00, 8) == 0x00
        assert cpu.sign_extend(0x01, 8) == 0x01
        
    def test_sign_extend_negative_8_bit(self, cpu):
        """Test sign extending negative 8-bit values"""
        assert cpu.sign_extend(0x80, 8) == 0xFFFFFF80
        assert cpu.sign_extend(0xFF, 8) == 0xFFFFFFFF
        assert cpu.sign_extend(0xFE, 8) == 0xFFFFFFFE
        
    def test_sign_extend_positive_12_bit(self, cpu):
        """Test sign extending positive 12-bit values"""
        assert cpu.sign_extend(0x7FF, 12) == 0x7FF
        assert cpu.sign_extend(0x100, 12) == 0x100
        
    def test_sign_extend_negative_12_bit(self, cpu):
        """Test sign extending negative 12-bit values"""
        assert cpu.sign_extend(0x800, 12) == 0xFFFFF800
        assert cpu.sign_extend(0xFFF, 12) == 0xFFFFFFFF
        
    def test_sign_extend_16_bit(self, cpu):
        """Test sign extending 16-bit values"""
        assert cpu.sign_extend(0x7FFF, 16) == 0x7FFF
        assert cpu.sign_extend(0x8000, 16) == 0xFFFF8000
        assert cpu.sign_extend(0xFFFF, 16) == 0xFFFFFFFF
        
    def test_to_signed_positive(self, cpu):
        """Test converting positive unsigned to signed"""
        assert cpu.to_signed(0) == 0
        assert cpu.to_signed(1) == 1
        assert cpu.to_signed(0x7FFFFFFF) == 0x7FFFFFFF
        
    def test_to_signed_negative(self, cpu):
        """Test converting negative unsigned to signed"""
        assert cpu.to_signed(0x80000000) == -0x80000000
        assert cpu.to_signed(0xFFFFFFFF) == -1
        assert cpu.to_signed(0xFFFFFFFE) == -2
        
    def test_to_unsigned_positive(self, cpu):
        """Test converting positive signed to unsigned"""
        assert cpu.to_unsigned(0) == 0
        assert cpu.to_unsigned(1) == 1
        assert cpu.to_unsigned(0x7FFFFFFF) == 0x7FFFFFFF
        
    def test_to_unsigned_negative(self, cpu):
        """Test converting negative signed to unsigned"""
        assert cpu.to_unsigned(-1) == 0xFFFFFFFF
        assert cpu.to_unsigned(-2) == 0xFFFFFFFE
        assert cpu.to_unsigned(-0x80000000) == 0x80000000


class TestCSROperations:
    """Test Control and Status Register operations"""
    
    def test_read_csr(self, cpu):
        """Test reading CSR registers"""
        assert cpu.read_csr(cpu.CSR_MSTATUS) == 0
        assert cpu.read_csr(cpu.CSR_MIE) == 0
        assert cpu.read_csr(cpu.CSR_MTVEC) == 0
        
    def test_write_csr(self, cpu):
        """Test writing CSR registers"""
        cpu.write_csr(cpu.CSR_MSTATUS, 0x12345678)
        assert cpu.read_csr(cpu.CSR_MSTATUS) == 0x12345678
        
        cpu.write_csr(cpu.CSR_MIE, 0xFFFFFFFF)
        assert cpu.read_csr(cpu.CSR_MIE) == 0xFFFFFFFF
        
    def test_write_csr_masked_to_32_bits(self, cpu):
        """Test CSR values are masked to 32 bits"""
        cpu.write_csr(cpu.CSR_MTVEC, 0x1FFFFFFFF)
        assert cpu.read_csr(cpu.CSR_MTVEC) == 0xFFFFFFFF
        
    def test_invalid_csr_address_raises_error(self, cpu):
        """Test invalid CSR addresses raise ValueError"""
        with pytest.raises(ValueError):
            cpu.read_csr(0xFFF)
        
        with pytest.raises(ValueError):
            cpu.write_csr(0x123, 100)
            
    def test_set_csr_bits(self, cpu):
        """Test atomic set bits operation"""
        cpu.write_csr(cpu.CSR_MIE, 0x00000001)
        old_value = cpu.set_csr_bits(cpu.CSR_MIE, 0x00000080)
        
        assert old_value == 0x00000001
        assert cpu.read_csr(cpu.CSR_MIE) == 0x00000081
        
    def test_clear_csr_bits(self, cpu):
        """Test atomic clear bits operation"""
        cpu.write_csr(cpu.CSR_MIE, 0x000000FF)
        old_value = cpu.clear_csr_bits(cpu.CSR_MIE, 0x000000F0)
        
        assert old_value == 0x000000FF
        assert cpu.read_csr(cpu.CSR_MIE) == 0x0000000F
        
    def test_write_mstatus_updates_interrupt_enabled(self, cpu):
        """Test writing mstatus updates interrupt_enabled flag"""
        assert cpu.interrupt_enabled is False
        
        cpu.write_csr(cpu.CSR_MSTATUS, cpu.MSTATUS_MIE)
        assert cpu.interrupt_enabled is True
        
        cpu.write_csr(cpu.CSR_MSTATUS, 0)
        assert cpu.interrupt_enabled is False


class TestInterruptControl:
    """Test interrupt enable/disable and global state"""
    
    def test_enable_interrupts(self, cpu):
        """Test enabling interrupts globally"""
        assert cpu.interrupt_enabled is False
        
        cpu.enable_interrupts()
        
        assert cpu.interrupt_enabled is True
        assert (cpu.read_csr(cpu.CSR_MSTATUS) & cpu.MSTATUS_MIE) != 0
        
    def test_disable_interrupts(self, cpu):
        """Test disabling interrupts globally"""
        cpu.enable_interrupts()
        assert cpu.interrupt_enabled is True
        
        cpu.disable_interrupts()
        
        assert cpu.interrupt_enabled is False
        assert (cpu.read_csr(cpu.CSR_MSTATUS) & cpu.MSTATUS_MIE) == 0
        
    def test_set_interrupt_pending(self, cpu):
        """Test setting interrupt pending bits"""
        cpu.set_interrupt_pending(cpu.MIE_MTIE)
        
        mip = cpu.read_csr(cpu.CSR_MIP)
        assert (mip & cpu.MIE_MTIE) != 0
        
    def test_clear_interrupt_pending(self, cpu):
        """Test clearing interrupt pending bits"""
        cpu.set_interrupt_pending(cpu.MIE_MTIE)
        cpu.clear_interrupt_pending(cpu.MIE_MTIE)
        
        mip = cpu.read_csr(cpu.CSR_MIP)
        assert (mip & cpu.MIE_MTIE) == 0
        
    def test_multiple_interrupts_pending(self, cpu):
        """Test multiple interrupt types can be pending simultaneously"""
        cpu.set_interrupt_pending(cpu.MIE_MTIE)
        cpu.set_interrupt_pending(cpu.MIE_RTIE)
        
        mip = cpu.read_csr(cpu.CSR_MIP)
        assert (mip & cpu.MIE_MTIE) != 0
        assert (mip & cpu.MIE_RTIE) != 0


class TestInterruptDetection:
    """Test interrupt pending detection logic"""
    
    def test_no_pending_interrupts_when_disabled(self, cpu):
        """Test no interrupts detected when globally disabled"""
        cpu.write_csr(cpu.CSR_MIE, 0xFF)  # Enable all interrupt sources
        cpu.write_csr(cpu.CSR_MIP, 0xFF)  # Set all pending
        cpu.disable_interrupts()
        
        assert cpu.has_pending_interrupts() is False
        
    def test_no_pending_interrupts_when_none_enabled(self, cpu):
        """Test no interrupts detected when none enabled"""
        cpu.enable_interrupts()
        cpu.write_csr(cpu.CSR_MIE, 0)  # No interrupt sources enabled
        cpu.write_csr(cpu.CSR_MIP, 0xFF)  # Set all pending
        
        assert cpu.has_pending_interrupts() is False
        
    def test_no_pending_interrupts_when_none_pending(self, cpu):
        """Test no interrupts detected when none pending"""
        cpu.enable_interrupts()
        cpu.write_csr(cpu.CSR_MIE, 0xFF)  # Enable all sources
        cpu.write_csr(cpu.CSR_MIP, 0)  # None pending
        
        assert cpu.has_pending_interrupts() is False
        
    def test_pending_interrupt_detected(self, cpu):
        """Test interrupt detected when enabled and pending"""
        cpu.enable_interrupts()
        cpu.write_csr(cpu.CSR_MIE, cpu.MIE_MTIE)  # Enable timer
        cpu.set_interrupt_pending(cpu.MIE_MTIE)  # Set timer pending
        
        assert cpu.has_pending_interrupts() is True
        
    def test_get_highest_priority_interrupt_none(self, cpu):
        """Test getting interrupt when none pending"""
        cpu.enable_interrupts()
        assert cpu.get_highest_priority_interrupt() is None
        
    def test_get_highest_priority_timer(self, cpu):
        """Test getting cycle-based timer interrupt"""
        cpu.enable_interrupts()
        cpu.write_csr(cpu.CSR_MIE, cpu.MIE_MTIE)
        cpu.set_interrupt_pending(cpu.MIE_MTIE)
        
        assert cpu.get_highest_priority_interrupt() == cpu.INT_TIMER
        
    def test_get_highest_priority_rt_timer(self, cpu):
        """Test getting real-time timer interrupt"""
        cpu.enable_interrupts()
        cpu.write_csr(cpu.CSR_MIE, cpu.MIE_RTIE)
        cpu.set_interrupt_pending(cpu.MIE_RTIE)
        
        assert cpu.get_highest_priority_interrupt() == cpu.INT_TIMER_REALTIME
        
    def test_rt_timer_has_higher_priority(self, cpu):
        """Test RT timer has higher priority than cycle timer"""
        cpu.enable_interrupts()
        cpu.write_csr(cpu.CSR_MIE, cpu.MIE_MTIE | cpu.MIE_RTIE)
        cpu.set_interrupt_pending(cpu.MIE_MTIE)
        cpu.set_interrupt_pending(cpu.MIE_RTIE)
        
        # Should return RT timer (higher priority)
        assert cpu.get_highest_priority_interrupt() == cpu.INT_TIMER_REALTIME


class TestInterruptHandling:
    """Test interrupt entry and return mechanisms"""
    
    def test_enter_interrupt_saves_pc(self, cpu):
        """Test entering interrupt saves PC to MEPC"""
        cpu.pc = 0x1234
        cpu.enable_interrupts()
        cpu.write_csr(cpu.CSR_MTVEC, 0x8000)
        
        cpu.enter_interrupt(cpu.INT_TIMER)
        
        assert cpu.read_csr(cpu.CSR_MEPC) == 0x1234
        
    def test_enter_interrupt_saves_cause(self, cpu):
        """Test entering interrupt saves cause to MCAUSE"""
        cpu.enable_interrupts()
        cpu.write_csr(cpu.CSR_MTVEC, 0x8000)
        
        cpu.enter_interrupt(cpu.INT_TIMER)
        
        assert cpu.read_csr(cpu.CSR_MCAUSE) == cpu.INT_TIMER
        
    def test_enter_interrupt_disables_interrupts(self, cpu):
        """Test entering interrupt disables global interrupts"""
        cpu.enable_interrupts()
        cpu.write_csr(cpu.CSR_MTVEC, 0x8000)
        
        assert cpu.interrupt_enabled is True
        
        cpu.enter_interrupt(cpu.INT_TIMER)
        
        assert cpu.interrupt_enabled is False
        
    def test_enter_interrupt_jumps_to_handler(self, cpu):
        """Test entering interrupt jumps PC to handler"""
        cpu.pc = 0x1000
        cpu.enable_interrupts()
        cpu.write_csr(cpu.CSR_MTVEC, 0x8000)
        
        cpu.enter_interrupt(cpu.INT_TIMER)
        
        assert cpu.pc == 0x8000
        
    def test_return_from_interrupt_restores_pc(self, cpu):
        """Test MRET restores PC from MEPC"""
        cpu.pc = 0x1234
        cpu.enable_interrupts()
        cpu.write_csr(cpu.CSR_MTVEC, 0x8000)
        
        cpu.enter_interrupt(cpu.INT_TIMER)
        assert cpu.pc == 0x8000
        
        cpu.return_from_interrupt()
        
        assert cpu.pc == 0x1234
        
    def test_return_from_interrupt_enables_interrupts(self, cpu):
        """Test MRET re-enables interrupts"""
        cpu.enable_interrupts()
        cpu.write_csr(cpu.CSR_MTVEC, 0x8000)
        
        cpu.enter_interrupt(cpu.INT_TIMER)
        assert cpu.interrupt_enabled is False
        
        cpu.return_from_interrupt()
        
        assert cpu.interrupt_enabled is True


class TestWaitForInterrupt:
    """Test WFI (Wait For Interrupt) functionality"""
    
    def test_wait_for_interrupt(self, cpu):
        """Test WFI sets waiting state"""
        assert cpu.waiting_for_interrupt is False
        
        cpu.wait_for_interrupt()
        
        assert cpu.waiting_for_interrupt is True
        
    def test_wake_from_wait(self, cpu):
        """Test waking from WFI state"""
        cpu.wait_for_interrupt()
        assert cpu.waiting_for_interrupt is True
        
        cpu.wake_from_wait()
        
        assert cpu.waiting_for_interrupt is False
        
    def test_wfi_cleared_on_reset(self, cpu):
        """Test WFI state is cleared on reset"""
        cpu.wait_for_interrupt()
        assert cpu.waiting_for_interrupt is True
        
        cpu.reset()
        
        assert cpu.waiting_for_interrupt is False


class TestRegisterDump:
    """Test register dump utility"""
    
    def test_dump_registers_format(self, cpu):
        """Test register dump produces expected format"""
        cpu.write_register(5, 0x12345678)
        cpu.write_register(10, 0xDEADBEEF)
        cpu.pc = 0x1000
        cpu.instruction_count = 42
        
        dump = cpu.dump_registers()
        
        assert "PC: 0x00001000" in dump
        assert "Instructions: 42" in dump
        assert "0x12345678" in dump
        assert "0xDEADBEEF" in dump
