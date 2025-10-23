"""
Unit tests for J (Jump) pseudo-instruction
Tests that J correctly expands to JAL zero, label
"""

import pytest
from src.assembler import Assembler, AssemblerError
from src.instruction import InstructionType
from src.vm import VirtualMachine


class TestJPseudoInstruction:
    """Test J pseudo-instruction parsing and expansion"""
    
    def test_j_expands_to_jal_zero(self, assembler):
        """Test that J expands to JAL with zero register"""
        program = """
.text
    J target
    ADDI x1, x1, 1
target:
    ADDI x2, x2, 2
    HALT
"""
        instructions = assembler.assemble(program)
        
        # First instruction should be JAL
        assert instructions[0].opcode == "JAL"
        assert instructions[0].rd == 0  # zero register
        assert instructions[0].label == "target"
    
    def test_j_basic_jump(self, vm):
        """Test basic jump to a label"""
        program = """
.text
    ADDI x10, x0, 1   # Should execute
    J skip            # Jump over next instruction
    ADDI x11, x0, 2   # Should NOT execute
skip:
    ADDI x12, x0, 3   # Should execute
    HALT
"""
        vm.load_program(program)
        vm.run()
        
        assert vm.cpu.read_register(10) == 1   # x10 was set
        assert vm.cpu.read_register(11) == 0   # x11 was NOT set (skipped)
        assert vm.cpu.read_register(12) == 3   # x12 was set
    
    def test_j_forward_jump(self, vm):
        """Test jumping forward in code"""
        program = """
.text
    ADDI x10, x0, 10
    J forward
    ADDI x11, x0, 20   # Skipped
    ADDI x12, x0, 30   # Skipped
forward:
    ADDI x13, x0, 40
    HALT
"""
        vm.load_program(program)
        vm.run()
        
        assert vm.cpu.read_register(10) == 10
        assert vm.cpu.read_register(11) == 0   # Skipped
        assert vm.cpu.read_register(12) == 0   # Skipped
        assert vm.cpu.read_register(13) == 40
    
    def test_j_backward_jump(self, vm):
        """Test jumping backward in code (simple loop)"""
        program = """
.text
    ADDI x1, x0, 0     # Counter
    ADDI x2, x0, 3     # Limit
loop:
    ADDI x1, x1, 1     # Increment counter
    BLT x1, x2, loop   # Loop if counter < limit
    HALT
"""
        vm.load_program(program)
        vm.run()
        
        assert vm.cpu.read_register(1) == 3   # Counter should reach limit
    
    def test_j_with_multiple_jumps(self, vm):
        """Test program with multiple J instructions"""
        program = """
.text
    ADDI x1, x0, 1
    J label2
label1:
    ADDI x3, x0, 3
    J end
label2:
    ADDI x2, x0, 2
    J label1
end:
    HALT
"""
        vm.load_program(program)
        vm.run()
        
        # Execution order: x1=1, jump to label2, x2=2, jump to label1, x3=3, jump to end
        assert vm.cpu.read_register(1) == 1
        assert vm.cpu.read_register(2) == 2
        assert vm.cpu.read_register(3) == 3
    
    def test_j_does_not_modify_ra(self, vm):
        """Test that J does not save return address (unlike CALL)"""
        program = """
.text
    ADDI x1, x0, 100   # Set ra (x1) to a known value
    J target
    ADDI x2, x0, 200
target:
    ADDI x3, x0, 300
    HALT
"""
        vm.load_program(program)
        vm.run()
        
        # ra should still have the value we set, not a return address
        assert vm.cpu.read_register(1) == 100  # ra unchanged
        assert vm.cpu.read_register(3) == 300
    
    def test_j_vs_call_difference(self, vm):
        """Test that J and CALL behave differently"""
        program_j = """
.text
    J target
    HALT
target:
    ADDI x10, x0, 1
    HALT
"""
        program_call = """
.text
    CALL target
    HALT
target:
    ADDI x11, x0, 2
    RET
"""
        # Test with J
        vm.load_program(program_j)
        vm.run()
        ra_after_j = vm.cpu.read_register(1)  # ra
        x10_after_j = vm.cpu.read_register(10)  # x10 should be set
        
        # Test with CALL
        vm2 = VirtualMachine()
        vm2.load_program(program_call)
        vm2.run()
        ra_after_call = vm2.cpu.read_register(1)  # ra
        x11_after_call = vm2.cpu.read_register(11)  # x11 should be set
        
        # J should not modify ra (stays 0), CALL should save return address
        assert ra_after_j == 0
        assert x10_after_j == 1  # J reached target
        assert ra_after_call != 0  # CALL saves return address
        assert x11_after_call == 2  # CALL reached target
    
    def test_j_requires_label(self, assembler):
        """Test that J requires a label operand"""
        program = """
.text
    J
    HALT
"""
        with pytest.raises(AssemblerError, match="J requires 1 operand"):
            assembler.assemble(program)
    
    def test_j_undefined_label(self, assembler):
        """Test error handling for undefined label"""
        program = """
.text
    J undefined_label
    HALT
"""
        with pytest.raises(AssemblerError, match="Undefined label"):
            assembler.assemble(program)
    
    def test_j_in_conditional_logic(self, vm):
        """Test J in conditional branching logic"""
        program = """
.text
    ADDI x1, x0, 5
    ADDI x2, x0, 10
    
    BLT x1, x2, is_less
    ADDI x3, x0, 1      # x1 >= x2
    J end
    
is_less:
    ADDI x3, x0, 2      # x1 < x2
    
end:
    HALT
"""
        vm.load_program(program)
        vm.run()
        
        # Since 5 < 10, should take is_less path
        assert vm.cpu.read_register(3) == 2
    
    def test_j_with_loop_structure(self, vm):
        """Test J used to exit from a loop"""
        program = """
.text
    ADDI x1, x0, 0     # Counter
    ADDI x2, x0, 5     # Limit
    
loop:
    ADDI x1, x1, 1     # Increment
    
    # Exit loop if counter >= limit
    BGE x1, x2, exit_loop
    J loop
    
exit_loop:
    ADDI x3, x0, 100   # Set flag
    HALT
"""
        vm.load_program(program)
        vm.run()
        
        assert vm.cpu.read_register(1) == 5   # Counter
        assert vm.cpu.read_register(3) == 100 # Flag set
    
    def test_j_offset_calculation(self, assembler):
        """Test that J correctly calculates relative offset"""
        program = """
.text
    ADDI x1, x0, 1
    ADDI x2, x0, 2
    J target
    ADDI x3, x0, 3
    ADDI x4, x0, 4
target:
    ADDI x5, x0, 5
    HALT
"""
        instructions = assembler.assemble(program)
        
        # Find the JAL instruction (expanded from J)
        jal_inst = None
        for inst in instructions:
            if inst.opcode == "JAL" and inst.rd == 0:
                jal_inst = inst
                break
        
        assert jal_inst is not None
        # Offset should be positive (forward jump)
        assert jal_inst.imm > 0
