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
