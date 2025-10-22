"""
Unit tests for Assembler module
Tests instruction parsing, label resolution, and error handling
"""

import pytest
from src.assembler import Assembler, AssemblerError
from src.instruction import InstructionType


class TestAssemblerBasics:
    """Test basic assembler initialization"""
    
    def test_assembler_initialization(self, assembler):
        """Test assembler initializes"""
        assert assembler is not None
        assert assembler.get_labels() == {}


class TestInstructionParsing:
    """Test parsing different instruction types"""
    
    def test_parse_r_type(self, assembler):
        """Test parsing R-type instructions"""
        instructions = assembler.assemble("ADD x1, x2, x3")
        assert len(instructions) == 1
        assert instructions[0].opcode == "ADD"
        assert instructions[0].type == InstructionType.R_TYPE
        assert instructions[0].rd == 1
        assert instructions[0].rs1 == 2
        assert instructions[0].rs2 == 3
        
    def test_parse_i_type(self, assembler):
        """Test parsing I-type instructions"""
        instructions = assembler.assemble("ADDI x1, x2, 100")
        assert len(instructions) == 1
        assert instructions[0].opcode == "ADDI"
        assert instructions[0].type == InstructionType.I_TYPE
        assert instructions[0].rd == 1
        assert instructions[0].rs1 == 2
        assert instructions[0].imm == 100
        
    def test_parse_load(self, assembler):
        """Test parsing load instructions"""
        instructions = assembler.assemble("LW x1, 4(x2)")
        assert len(instructions) == 1
        assert instructions[0].opcode == "LW"
        assert instructions[0].rd == 1
        assert instructions[0].rs1 == 2
        assert instructions[0].imm == 4
        
    def test_parse_store(self, assembler):
        """Test parsing store instructions"""
        instructions = assembler.assemble("SW x1, 8(x2)")
        assert len(instructions) == 1
        assert instructions[0].opcode == "SW"
        assert instructions[0].type == InstructionType.S_TYPE
        
    def test_parse_branch(self, assembler):
        """Test parsing branch instructions"""
        instructions = assembler.assemble("BEQ x1, x2, 16")
        assert len(instructions) == 1
        assert instructions[0].opcode == "BEQ"
        assert instructions[0].type == InstructionType.B_TYPE
        
    def test_parse_jump(self, assembler):
        """Test parsing jump instructions"""
        instructions = assembler.assemble("JAL x1, 100")
        assert len(instructions) == 1
        assert instructions[0].opcode == "JAL"
        assert instructions[0].type == InstructionType.J_TYPE
        
    def test_parse_lui(self, assembler):
        """Test parsing LUI instruction"""
        instructions = assembler.assemble("LUI x1, 0x12345")
        assert len(instructions) == 1
        assert instructions[0].opcode == "LUI"
        assert instructions[0].type == InstructionType.U_TYPE
        
    def test_parse_halt(self, assembler):
        """Test parsing HALT instruction"""
        instructions = assembler.assemble("HALT")
        assert len(instructions) == 1
        assert instructions[0].opcode == "HALT"
        assert instructions[0].type == InstructionType.HALT


class TestLabelSupport:
    """Test label definition and resolution"""
    
    def test_define_and_use_label(self, assembler):
        """Test defining and using labels"""
        program = """
loop:
    ADDI x1, x1, 1
    BEQ x1, x2, loop
"""
        instructions = assembler.assemble(program)
        labels = assembler.get_labels()
        
        assert "loop" in labels
        assert labels["loop"] == 0  # First instruction
        
    def test_forward_reference(self, assembler):
        """Test forward label references"""
        program = """
    JAL x1, target
    ADDI x1, x1, 1
target:
    ADDI x2, x2, 1
"""
        instructions = assembler.assemble(program)
        labels = assembler.get_labels()
        
        assert "target" in labels
        # Jump should reference correct address
        
    def test_multiple_labels(self, assembler):
        """Test multiple label definitions"""
        program = """
start:
    ADDI x1, x0, 1
middle:
    ADDI x2, x0, 2
end:
    HALT
"""
        instructions = assembler.assemble(program)
        labels = assembler.get_labels()
        
        assert "start" in labels
        assert "middle" in labels
        assert "end" in labels


class TestComments:
    """Test comment handling"""
    
    def test_full_line_comment(self, assembler):
        """Test full-line comments"""
        program = """
# This is a comment
ADDI x1, x0, 1
"""
        instructions = assembler.assemble(program)
        assert len(instructions) == 1
        
    def test_inline_comment(self, assembler):
        """Test inline comments"""
        program = "ADDI x1, x0, 1  # Set x1 to 1"
        instructions = assembler.assemble(program)
        assert len(instructions) == 1
        assert instructions[0].opcode == "ADDI"


class TestErrorHandling:
    """Test assembler error handling"""
    
    def test_invalid_instruction(self, assembler):
        """Test invalid instruction raises error"""
        with pytest.raises(AssemblerError):
            assembler.assemble("INVALID x1, x2, x3")
            
    def test_undefined_label(self, assembler):
        """Test undefined label raises error"""
        with pytest.raises(AssemblerError):
            assembler.assemble("JAL x1, undefined_label")
            
    def test_invalid_register(self, assembler):
        """Test invalid register raises error"""
        with pytest.raises(AssemblerError):
            assembler.assemble("ADDI x99, x0, 1")


class TestABIRegisterNames:
    """Test RISC-V ABI register name support"""
    
    def test_parse_abi_names_r_type(self, assembler):
        """Test R-type instructions with ABI names"""
        instructions = assembler.assemble("ADD a0, t0, t1")
        assert len(instructions) == 1
        assert instructions[0].rd == 10  # a0 = x10
        assert instructions[0].rs1 == 5  # t0 = x5
        assert instructions[0].rs2 == 6  # t1 = x6
        
    def test_parse_abi_names_i_type(self, assembler):
        """Test I-type instructions with ABI names"""
        instructions = assembler.assemble("ADDI sp, sp, -16")
        assert len(instructions) == 1
        assert instructions[0].rd == 2   # sp = x2
        assert instructions[0].rs1 == 2  # sp = x2
        assert instructions[0].imm == -16
        
    def test_parse_abi_names_load_store(self, assembler):
        """Test load/store with ABI names"""
        instructions = assembler.assemble("SW a0, 0(sp)")
        assert len(instructions) == 1
        assert instructions[0].rs2 == 10  # a0 = x10
        assert instructions[0].rs1 == 2   # sp = x2
        
        instructions = assembler.assemble("LW a1, 4(sp)")
        assert len(instructions) == 1
        assert instructions[0].rd == 11   # a1 = x11
        assert instructions[0].rs1 == 2   # sp = x2
        
    def test_parse_all_temporary_registers(self, assembler):
        """Test all temporary register names (t0-t6)"""
        # t0-t2
        for i, reg_num in [(0, 5), (1, 6), (2, 7)]:
            instructions = assembler.assemble(f"ADDI t{i}, zero, {i}")
            assert instructions[0].rd == reg_num
        
        # t3-t6
        for i, reg_num in [(3, 28), (4, 29), (5, 30), (6, 31)]:
            instructions = assembler.assemble(f"ADDI t{i}, zero, {i}")
            assert instructions[0].rd == reg_num
    
    def test_parse_all_saved_registers(self, assembler):
        """Test all saved register names (s0-s11)"""
        saved_mapping = {
            0: 8, 1: 9, 2: 18, 3: 19, 4: 20, 5: 21,
            6: 22, 7: 23, 8: 24, 9: 25, 10: 26, 11: 27
        }
        for s_num, x_num in saved_mapping.items():
            instructions = assembler.assemble(f"ADDI s{s_num}, zero, {s_num}")
            assert instructions[0].rd == x_num
    
    def test_parse_all_argument_registers(self, assembler):
        """Test all argument register names (a0-a7)"""
        for i in range(8):
            instructions = assembler.assemble(f"ADDI a{i}, zero, {i}")
            assert instructions[0].rd == 10 + i  # a0-a7 = x10-x17
    
    def test_mixed_notation_in_program(self, assembler):
        """Test mixing x-notation and ABI names in same program"""
        program = """
    ADDI a0, zero, 42    # Use ABI name
    ADDI x11, a0, 1      # Mix both
    ADD t0, x10, x11     # Mix both
    SW a0, 0(sp)         # Use ABI names
"""
        instructions = assembler.assemble(program)
        assert len(instructions) == 4
        
        # Check first instruction: ADDI a0, zero, 42
        assert instructions[0].rd == 10    # a0
        assert instructions[0].rs1 == 0    # zero
        
        # Check second instruction: ADDI x11, a0, 1
        assert instructions[1].rd == 11    # x11
        assert instructions[1].rs1 == 10   # a0
        
        # Check third instruction: ADD t0, x10, x11
        assert instructions[2].rd == 5     # t0
        assert instructions[2].rs1 == 10   # x10
        assert instructions[2].rs2 == 11   # x11
    
    def test_case_insensitive_abi_names(self, assembler):
        """Test ABI names are case-insensitive"""
        instructions = assembler.assemble("ADD A0, T0, S1")
        assert instructions[0].rd == 10    # a0
        assert instructions[0].rs1 == 5    # t0
        assert instructions[0].rs2 == 9    # s1
    
    def test_fp_alias(self, assembler):
        """Test fp as alias for s0"""
        # fp and s0 should both map to x8
        instructions = assembler.assemble("ADDI fp, zero, 100")
        assert instructions[0].rd == 8
        
        instructions = assembler.assemble("ADDI s0, zero, 100")
        assert instructions[0].rd == 8


class TestMultipleInstructions:
    """Test assembling multiple instructions"""
    
    def test_assemble_program(self, assembler):
        """Test assembling complete program"""
        program = """
    ADDI x1, x0, 10
    ADDI x2, x0, 20
    ADD x3, x1, x2
    HALT
"""
        instructions = assembler.assemble(program)
        assert len(instructions) == 4
        assert instructions[0].opcode == "ADDI"
        assert instructions[1].opcode == "ADDI"
        assert instructions[2].opcode == "ADD"
        assert instructions[3].opcode == "HALT"


class TestPseudoInstructions:
    """Test pseudo-instruction expansion"""
    
    def test_call_expands_to_jal_ra(self, assembler):
        """Test CALL label expands to JAL ra, label"""
        program = """
main:
    CALL helper
    HALT
helper:
    ADDI x1, x0, 42
"""
        instructions = assembler.assemble(program)
        
        # CALL should expand to JAL
        assert instructions[0].opcode == "JAL"
        assert instructions[0].rd == 1  # ra register
        # Label should be resolved to helper function
        assert instructions[0].imm == 8  # Offset to helper (2 instructions * 4 bytes)
    
    def test_ret_expands_to_jalr(self, assembler):
        """Test RET expands to JALR zero, ra, 0"""
        program = """
    ADDI x1, x0, 42
    RET
"""
        instructions = assembler.assemble(program)
        
        # RET should expand to JALR
        assert instructions[1].opcode == "JALR"
        assert instructions[1].rd == 0   # zero register (discard return address)
        assert instructions[1].rs1 == 1  # ra register
        assert instructions[1].imm == 0  # No offset
    
    def test_call_ret_function_pattern(self, assembler):
        """Test typical CALL/RET function pattern"""
        program = """
main:
    ADDI a0, zero, 5
    CALL square
    HALT

square:
    MUL a0, a0, a0
    RET
"""
        instructions = assembler.assemble(program)
        
        # Should be 4 instructions: ADDI, JAL (from CALL), HALT, MUL, JALR (from RET)
        assert len(instructions) == 5
        
        # Check CALL expanded to JAL
        assert instructions[1].opcode == "JAL"
        assert instructions[1].rd == 1  # ra
        
        # Check RET expanded to JALR
        assert instructions[4].opcode == "JALR"
        assert instructions[4].rd == 0   # zero
        assert instructions[4].rs1 == 1  # ra
        assert instructions[4].imm == 0
    
    def test_nested_calls_with_call_ret(self, assembler):
        """Test nested function calls using CALL/RET"""
        program = """
main:
    CALL func1
    HALT

func1:
    CALL func2
    RET

func2:
    ADDI x1, x0, 1
    RET
"""
        instructions = assembler.assemble(program)
        
        # main: CALL func1, HALT
        # func1: CALL func2, RET
        # func2: ADDI, RET
        # Total: 6 instructions
        assert len(instructions) == 6
        
        # First CALL
        assert instructions[0].opcode == "JAL"
        
        # Second CALL
        assert instructions[2].opcode == "JAL"
        
        # First RET
        assert instructions[3].opcode == "JALR"
        
        # Second RET
        assert instructions[5].opcode == "JALR"
    
    def test_call_with_abi_names(self, assembler):
        """Test CALL works with program using ABI register names"""
        program = """
main:
    ADDI a0, zero, 42
    CALL print_value
    HALT

print_value:
    SW a0, 0(sp)
    RET
"""
        instructions = assembler.assemble(program)
        
        # Verify CALL expanded correctly
        assert instructions[1].opcode == "JAL"
        assert instructions[1].rd == 1  # ra
        
        # Verify RET expanded correctly
        assert instructions[4].opcode == "JALR"
