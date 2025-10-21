"""
Unit tests for exception reporting functionality
Tests that exceptions contain all expected debugging information
"""

import pytest
from src.vm import VirtualMachine, VMError
from src.memory import MemoryAccessError, MemoryProtectionError
from src.debugger import CPUDebugger, format_exception_report


class TestExceptionReporting:
    """Test that exceptions are raised with comprehensive debugging information"""
    
    def test_memory_access_out_of_bounds_exception(self):
        """Test that out of bounds memory access generates detailed exception"""
        vm = VirtualMachine()
        
        # Program that tries to access memory way out of bounds
        program = """
        LUI x7, 0x10000       # x7 = 0x10000000 (way out of bounds)
        LW x8, 0(x7)          # This should trigger exception
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error = exc_info.value
        error_str = str(error)
        
        # Check that detailed report is generated
        assert "CPU EXCEPTION" in error_str
        assert "Exception Type:" in error_str
        assert "MemoryAccessError" in error_str
        assert "Category:" in error_str
        assert "Memory Access Violation" in error_str
        
        # Check for hints
        assert "Hints:" in error_str
        assert "outside valid memory range" in error_str.lower()
        
        # Check for instruction context
        assert "Instruction Context:" in error_str
        assert "EXCEPTION HERE" in error_str
        assert "LW" in error_str
        
        # Check for register dump
        assert "Register State:" in error_str
        assert "x 7" in error_str
        assert "0x10000000" in error_str  # The invalid address in register
        
        # Check for stack state
        assert "Stack State" in error_str
        assert "SP:" in error_str
        
        # Check for CSR dump
        assert "Control and Status Registers" in error_str
        assert "MSTATUS" in error_str
        
        # Check for memory region analysis
        assert "Memory Region Analysis:" in error_str
        assert "OUT OF BOUNDS" in error_str
        
        # Check for memory dump
        assert "Memory dump around" in error_str
        
        # Verify fault address was captured
        assert error.fault_address is not None
        assert error.fault_address == 0x10000000
    
    def test_unaligned_memory_access_exception(self):
        """Test that unaligned memory access generates detailed exception"""
        vm = VirtualMachine()
        
        # Program with unaligned memory access
        program = """
        ADDI x5, x0, 0x10001  # Unaligned address
        LW x6, 0(x5)          # Should trigger alignment error
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Check for alignment-specific information
        assert "MemoryAccessError" in error_str
        assert "Unaligned" in error_str or "aligned" in error_str
        assert "4-byte" in error_str or "must be" in error_str
        
        # Check that hints mention alignment
        assert "aligned" in error_str.lower()
    
    def test_memory_protection_violation_exception(self):
        """Test that write to protected memory generates detailed exception"""
        vm = VirtualMachine(protect_text=True)
        
        # Program that tries to write to text segment
        program = """
        ADDI x5, x0, 100
        ADDI x8, x0, 0        # x8 = 0 (text segment address)
        SW x5, 0(x8)          # Should trigger protection error
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Check for protection-specific information
        assert "MemoryProtectionError" in error_str
        assert "Memory Protection Violation" in error_str
        assert "protected" in error_str.lower() or "read-only" in error_str.lower()
        
        # Check for helpful hints
        assert "text segment" in error_str.lower()
        
        # Check that memory region shows text segment
        assert "TEXT SEGMENT" in error_str
    
    def test_pc_out_of_bounds_exception(self):
        """Test that PC out of bounds generates detailed exception"""
        vm = VirtualMachine()
        
        # Program that jumps to invalid address
        program = """
        LUI x5, 0x10000       # x5 = 0x10000000
        JALR x1, x5, 0        # Jump to way out of bounds
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Check for PC-related information
        assert "PC out of bounds" in error_str
        
        # Should still have register dump showing the jump target
        assert "Register State:" in error_str


class TestExceptionInformation:
    """Test that exception information is complete and accurate"""
    
    def test_exception_captures_cpu_state(self):
        """Test that exception captures CPU state at time of error"""
        vm = VirtualMachine()
        
        program = """
        ADDI x5, x0, 42
        ADDI x6, x0, 100
        ADDI x7, x0, 200
        LUI x8, 0x10000
        LW x9, 0(x8)          # Trigger exception
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error = exc_info.value
        
        # Verify CPU state was captured
        assert error.cpu is not None
        assert error.cpu.registers[5] == 42
        assert error.cpu.registers[6] == 100
        assert error.cpu.registers[7] == 200
        
        # Verify memory was captured
        assert error.memory is not None
        
        # Verify instructions were captured
        assert error.instructions is not None
        assert len(error.instructions) > 0
    
    def test_exception_shows_instruction_context(self):
        """Test that exception shows surrounding instructions"""
        vm = VirtualMachine()
        
        # Create program with identifiable instructions
        program = """
        ADDI x1, x0, 1
        ADDI x2, x0, 2
        ADDI x3, x0, 3
        LUI x7, 0x10000
        LW x8, 0(x7)          # Exception here - instruction 4
        ADDI x9, x0, 9
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Should show instructions before the fault
        assert "ADDI x3" in error_str  # 2 instructions before
        assert "LUI x7" in error_str   # 1 instruction before
        
        # Should show the faulting instruction with marker
        assert "LW x8" in error_str
        assert "EXCEPTION HERE" in error_str
        
        # Should show instruction after the fault
        assert "ADDI x9" in error_str
    
    def test_exception_shows_stack_usage(self):
        """Test that exception shows stack state with values"""
        vm = VirtualMachine()
        
        # Program that pushes values to stack then faults
        program = """
        ADDI x5, x0, 100
        ADDI x2, x2, -4       # Move SP down
        SW x5, 0(x2)          # Store 100 on stack
        
        ADDI x6, x0, 200
        ADDI x2, x2, -4
        SW x6, 0(x2)          # Store 200 on stack
        
        LUI x7, 0x10000
        LW x8, 0(x7)          # Trigger exception
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Check stack information is present
        assert "Stack State" in error_str
        assert "bytes used" in error_str
        
        # Check that stack values are shown
        assert "0x000BFFF" in error_str  # Stack addresses
        
        # The values we pushed should be visible in the dump
        # (100 = 0x64, 200 = 0xC8)
        assert "200" in error_str or "0x000000C8" in error_str
    
    def test_exception_shows_csr_state(self):
        """Test that exception shows CSR state"""
        vm = VirtualMachine()
        
        # Program that modifies CSRs then faults
        program = """
        # Enable interrupts
        ADDI x5, x0, 0x08     # MIE bit
        CSRRW x0, 0x300, x5   # Write to MSTATUS
        
        LUI x7, 0x10000
        LW x8, 0(x7)          # Trigger exception
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Check CSR information is present
        assert "Control and Status Registers" in error_str
        assert "MSTATUS" in error_str
        assert "MIE" in error_str
        assert "MTVEC" in error_str
        
        # Should show interrupt state
        assert "Machine Interrupt Enable" in error_str
        assert "Global interrupts:" in error_str


class TestExceptionClassification:
    """Test that exceptions are properly classified with helpful hints"""
    
    def test_out_of_bounds_classification(self):
        """Test classification of out of bounds errors"""
        vm = VirtualMachine()
        
        program = """
        LUI x7, 0x10000
        LW x8, 0(x7)
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Check classification
        assert "Category: Memory Access Violation" in error_str
        
        # Check for helpful hints
        assert "Hints:" in error_str
        assert "outside valid memory range" in error_str.lower()
    
    def test_alignment_error_classification(self):
        """Test classification of alignment errors"""
        vm = VirtualMachine()
        
        program = """
        ADDI x5, x0, 1
        LW x6, 0(x5)
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Check for alignment hints
        assert "aligned" in error_str.lower()
        assert "4-byte" in error_str or "must be" in error_str
    
    def test_protection_error_classification(self):
        """Test classification of protection errors"""
        vm = VirtualMachine(protect_text=True)
        
        program = """
        ADDI x5, x0, 0
        SW x5, 0(x5)
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Check classification
        assert "Category: Memory Protection Violation" in error_str
        
        # Check for helpful hints
        assert "read-only" in error_str.lower() or "protected" in error_str.lower()
        assert "text segment" in error_str.lower()


class TestDebuggerComponents:
    """Test individual debugger components"""
    
    def test_register_dump_format(self):
        """Test that register dump is properly formatted"""
        vm = VirtualMachine()
        
        # Set some recognizable register values
        vm.cpu.write_register(5, 0x12345678)
        vm.cpu.write_register(10, 0xDEADBEEF)
        vm.cpu.pc = 0x1234
        vm.cpu.instruction_count = 42
        
        debugger = CPUDebugger(vm.cpu, vm.memory, [])
        dump = debugger.dump_registers()
        
        # Check format
        assert "Register State:" in dump
        assert "x 5" in dump
        assert "0x12345678" in dump
        assert "x10" in dump
        assert "0xDEADBEEF" in dump
        assert "PC: 0x00001234" in dump
        assert "Instructions executed: 42" in dump
    
    def test_csr_dump_format(self):
        """Test that CSR dump is properly formatted"""
        vm = VirtualMachine()
        
        # Set some CSR values
        vm.cpu.write_csr(vm.cpu.CSR_MSTATUS, 0x08)  # Enable interrupts
        vm.cpu.write_csr(vm.cpu.CSR_MIE, 0x880)     # Enable timer interrupts
        
        debugger = CPUDebugger(vm.cpu, vm.memory, [])
        dump = debugger.dump_csrs()
        
        # Check format
        assert "Control and Status Registers" in dump
        assert "MSTATUS" in dump
        assert "MIE" in dump
        assert "Machine Interrupt Enable" in dump
        assert "ENABLED" in dump or "DISABLED" in dump
    
    def test_stack_dump_format(self):
        """Test that stack dump is properly formatted"""
        vm = VirtualMachine()
        
        # Push some values to stack
        sp = 0xBFFFC
        vm.cpu.write_register(2, sp - 12)
        vm.memory.write_word(sp - 12, 100)
        vm.memory.write_word(sp - 8, 200)
        vm.memory.write_word(sp - 4, 300)
        
        debugger = CPUDebugger(vm.cpu, vm.memory, [])
        dump = debugger.dump_stack()
        
        # Check format
        assert "Stack State" in dump
        assert "SP:" in dump
        assert "bytes used" in dump
        assert "Top" in dump and "words:" in dump
        
        # Should show stack pointer marker
        assert "→" in dump
    
    def test_instruction_context_format(self):
        """Test that instruction context is properly formatted"""
        vm = VirtualMachine()
        
        program = """
        ADDI x1, x0, 1
        ADDI x2, x0, 2
        ADDI x3, x0, 3
        ADDI x4, x0, 4
        ADDI x5, x0, 5
        HALT
        """
        
        vm.load_program(program)
        vm.cpu.pc = 8  # Point to 3rd instruction
        
        debugger = CPUDebugger(vm.cpu, vm.memory, vm.instructions)
        context = debugger.dump_instruction_context(window=2)
        
        # Check format
        assert "Instruction Context:" in context
        assert "[0x0000]" in context  # Address format
        assert "[0x0004]" in context
        assert "[0x0008]" in context
        assert "→" in context  # Current instruction marker
        assert "EXCEPTION HERE" in context
        assert "ADDI" in context
    
    def test_memory_region_analysis(self):
        """Test memory region analysis"""
        vm = VirtualMachine()
        debugger = CPUDebugger(vm.cpu, vm.memory, [])
        
        # Test text segment
        analysis = debugger.analyze_memory_region(0x5000)
        assert "TEXT SEGMENT" in analysis
        assert "program code" in analysis
        
        # Test data segment
        analysis = debugger.analyze_memory_region(0x20000)
        assert "DATA SEGMENT" in analysis
        
        # Test heap
        analysis = debugger.analyze_memory_region(0x50000)
        assert "HEAP" in analysis
        
        # Test stack
        analysis = debugger.analyze_memory_region(0xA0000)
        assert "STACK" in analysis
        
        # Test out of bounds
        analysis = debugger.analyze_memory_region(0x200000)
        assert "OUT OF BOUNDS" in analysis
    
    def test_memory_dump_format(self):
        """Test memory hexdump format"""
        vm = VirtualMachine()
        
        # Write some recognizable data
        addr = 0x10000
        vm.memory.write_word(addr, 0x12345678)
        vm.memory.write_word(addr + 4, 0xDEADBEEF)
        
        debugger = CPUDebugger(vm.cpu, vm.memory, [])
        dump = debugger.dump_memory_around(addr + 2, num_lines=3)
        
        # Check format
        assert "Memory dump around" in dump
        assert "[0x" in dump
        assert "]:" in dump
        assert "|" in dump  # ASCII section markers
        assert "→" in dump  # Fault line marker
    
    def test_interrupt_state_format(self):
        """Test interrupt state format"""
        vm = VirtualMachine()
        
        # Enable interrupts and set some state
        vm.cpu.enable_interrupts()
        vm.cpu.set_interrupt_pending(vm.cpu.MIE_MTIE)
        
        debugger = CPUDebugger(vm.cpu, vm.memory, [])
        state = debugger.dump_interrupt_state()
        
        # Check format
        assert "Interrupt and Timer State:" in state
        assert "Global interrupts:" in state
        assert "ENABLED" in state
        assert "Interrupt Pending:" in state
        assert "Cycle Timer" in state
        assert "Real-time Timer" in state


class TestExceptionWithDifferentStates:
    """Test exceptions with various CPU states"""
    
    def test_exception_with_interrupt_enabled(self):
        """Test exception report when interrupts are enabled"""
        vm = VirtualMachine()
        
        program = """
        # Enable interrupts
        ADDI x5, x0, 0x08
        CSRRW x0, 0x300, x5
        
        LUI x7, 0x10000
        LW x8, 0(x7)
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Should show that interrupts are enabled
        assert "Global interrupts: ENABLED" in error_str
    
    def test_exception_with_modified_sp(self):
        """Test exception report with modified stack pointer"""
        vm = VirtualMachine()
        
        program = """
        # Modify stack pointer
        ADDI x2, x2, -32
        
        LUI x7, 0x10000
        LW x8, 0(x7)
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Should show modified SP and usage
        assert "32 bytes used" in error_str or "36 bytes used" in error_str
    
    def test_exception_captures_original_exception(self):
        """Test that VMError captures the original exception"""
        vm = VirtualMachine()
        
        program = """
        LUI x7, 0x10000
        LW x8, 0(x7)
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error = exc_info.value
        
        # Should have captured the original MemoryAccessError
        assert error.original_exception is not None
        assert isinstance(error.original_exception, MemoryAccessError)


class TestExceptionEdgeCases:
    """Test exception reporting in edge cases"""
    
    def test_exception_on_first_instruction(self):
        """Test exception on the very first instruction"""
        vm = VirtualMachine()
        
        program = """
        LUI x7, 0x10000
        LW x8, 0(x7)
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Should still show instruction context
        assert "Instruction Context:" in error_str
        assert "LUI x7" in error_str
    
    def test_exception_with_empty_stack(self):
        """Test exception when stack hasn't been used"""
        vm = VirtualMachine()
        
        program = """
        LUI x7, 0x10000
        LW x8, 0(x7)
        HALT
        """
        
        vm.load_program(program)
        
        with pytest.raises(VMError) as exc_info:
            vm.run(max_instructions=100)
        
        error_str = str(exc_info.value)
        
        # Should show stack at initial position
        assert "Stack State" in error_str
        assert "0x000BFFFC" in error_str
    
    def test_format_exception_report_function(self):
        """Test the standalone format_exception_report function"""
        vm = VirtualMachine()
        
        program = """
        ADDI x5, x0, 42
        LUI x7, 0x10000
        LW x8, 0(x7)
        HALT
        """
        
        vm.load_program(program)
        
        # Run until exception
        try:
            vm.run(max_instructions=100)
        except VMError:
            pass
        
        # Generate report manually
        exception = MemoryAccessError("Test error at 0x10000000")
        report = format_exception_report(
            vm.cpu, 
            vm.memory, 
            vm.instructions,
            exception,
            fault_address=0x10000000
        )
        
        # Check all major sections are present
        assert "CPU EXCEPTION" in report
        assert "Register State:" in report
        assert "Control and Status Registers" in report
        assert "Stack State" in report
        assert "Instruction Context:" in report
        assert "Memory Region Analysis:" in report
        assert "Memory dump around" in report
        assert "Interrupt and Timer State:" in report
