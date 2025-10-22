"""
Unit tests for LA (Load Address) pseudo-instruction
Tests that LA correctly expands to LUI + ADDI and loads addresses properly
"""

import pytest
from src.assembler import Assembler, AssemblerError
from src.instruction import InstructionType


class TestLAPseudoInstruction:
    """Test LA pseudo-instruction parsing and expansion"""
    
    def test_la_expands_to_two_instructions(self, assembler):
        """Test that LA expands to LUI + ADDI"""
        program = """
.data
test_label: .word 42

.text
    LA x10, test_label
"""
        instructions = assembler.assemble(program)
        
        # LA should expand to 2 instructions
        assert len(instructions) == 2
        assert instructions[0].opcode == "LUI"
        assert instructions[1].opcode == "ADDI"
    
    def test_la_with_abi_names(self, assembler):
        """Test LA with ABI register names"""
        program = """
.data
msg: .string "Hello"

.text
    LA a0, msg
"""
        instructions = assembler.assemble(program)
        
        assert len(instructions) == 2
        assert instructions[0].opcode == "LUI"
        assert instructions[0].rd == 10  # a0 = x10
        assert instructions[1].opcode == "ADDI"
        assert instructions[1].rd == 10
        assert instructions[1].rs1 == 10  # ADDI a0, a0, offset
    
    def test_la_loads_correct_address(self, assembler):
        """Test that LA loads the correct data segment address"""
        program = """
.data
test_data: .word 0x12345678

.text
    LA x5, test_data
"""
        instructions = assembler.assemble(program)
        labels = assembler.get_labels()
        
        # Data section starts at 0x10000
        expected_addr = labels['test_data']
        assert expected_addr == 0x10000
        
        # LUI should load upper 20 bits
        lui_imm = instructions[0].imm
        assert lui_imm == (expected_addr >> 12) & 0xFFFFF
        
        # ADDI should load lower 12 bits
        addi_imm = instructions[1].imm
        assert addi_imm == expected_addr & 0xFFF
    
    def test_la_with_offset_address(self, assembler):
        """Test LA with an address that has non-zero lower bits"""
        program = """
.data
first: .word 1
second: .word 2
third: .word 3

.text
    LA x6, third
"""
        instructions = assembler.assemble(program)
        labels = assembler.get_labels()
        
        # third should be at 0x10008 (0x10000 + 8 bytes)
        expected_addr = labels['third']
        assert expected_addr == 0x10008
        
        # Verify the expansion
        lui_imm = instructions[0].imm
        addi_imm = instructions[1].imm
        
        # Reconstruct address
        reconstructed = (lui_imm << 12) | (addi_imm & 0xFFF)
        assert reconstructed == expected_addr
    
    def test_la_multiple_labels(self, assembler):
        """Test multiple LA instructions with different labels"""
        program = """
.data
str1: .string "First"
str2: .string "Second"

.text
    LA a0, str1
    LA a1, str2
"""
        instructions = assembler.assemble(program)
        labels = assembler.get_labels()
        
        # Should have 4 instructions (2 LA -> 4 instructions)
        assert len(instructions) == 4
        
        # First LA (a0 = x10)
        assert instructions[0].opcode == "LUI"
        assert instructions[0].rd == 10
        assert instructions[1].opcode == "ADDI"
        assert instructions[1].rd == 10
        
        # Second LA (a1 = x11)
        assert instructions[2].opcode == "LUI"
        assert instructions[2].rd == 11
        assert instructions[3].opcode == "ADDI"
        assert instructions[3].rd == 11
        
        # Verify addresses are different
        str1_addr = (instructions[0].imm << 12) | (instructions[1].imm & 0xFFF)
        str2_addr = (instructions[2].imm << 12) | (instructions[3].imm & 0xFFF)
        assert str1_addr != str2_addr
        assert str2_addr > str1_addr
    
    def test_la_with_text_label(self, assembler):
        """Test LA with a label in text section (function address)"""
        program = """
.text
main:
    LA x1, my_function
    JALR x0, x1, 0
    
my_function:
    ADDI x5, x5, 1
    JALR x0, x1, 0
"""
        instructions = assembler.assemble(program)
        labels = assembler.get_labels()
        
        # LA expands to 2 instructions (LUI + ADDI), plus JALR = 3 instructions
        # So my_function is at PC=12 (0, 4, 8, then 12)
        assert labels['my_function'] == 12
        
        # First two instructions are the LA expansion
        assert instructions[0].opcode == "LUI"
        assert instructions[1].opcode == "ADDI"
        
        # Verify the address loaded is correct (should be 12)
        loaded_addr = (instructions[0].imm << 12) | (instructions[1].imm & 0xFFF)
        assert loaded_addr == 12
    
    def test_la_preserves_register(self, assembler):
        """Test that LA's ADDI uses the same register as destination and source"""
        program = """
.data
data: .word 100

.text
    LA t0, data
"""
        instructions = assembler.assemble(program)
        
        # Both LUI and ADDI should use t0 (x5)
        assert instructions[0].rd == 5  # LUI t0, ...
        assert instructions[1].rd == 5  # ADDI t0, t0, ...
        assert instructions[1].rs1 == 5
    
    def test_la_with_undefined_label_error(self, assembler):
        """Test that LA with undefined label raises error"""
        program = """
.text
    LA x10, undefined_label
"""
        with pytest.raises(AssemblerError, match="Undefined label"):
            assembler.assemble(program)
    
    def test_la_requires_two_operands(self, assembler):
        """Test that LA requires exactly 2 operands"""
        program = """
.text
    LA x10
"""
        with pytest.raises(AssemblerError, match="requires 2 operands"):
            assembler.assemble(program)
    
    def test_la_with_string_data(self, assembler):
        """Test LA with string data labels"""
        program = """
.data
hello: .string "Hello, World!"
world: .string "Welcome!"

.text
    LA a0, hello
    LA a1, world
"""
        instructions = assembler.assemble(program)
        labels = assembler.get_labels()
        
        # hello at 0x10000, world at 0x1000E (14 bytes after)
        assert labels['hello'] == 0x10000
        assert labels['world'] == 0x1000E
        
        # Verify first LA loads 0x10000
        hello_addr = (instructions[0].imm << 12) | (instructions[1].imm & 0xFFF)
        assert hello_addr == 0x10000
        
        # Verify second LA loads 0x1000E
        world_addr = (instructions[2].imm << 12) | (instructions[3].imm & 0xFFF)
        assert world_addr == 0x1000E


class TestLAIntegration:
    """Integration tests for LA with actual VM execution"""
    
    def test_la_loads_correct_address_in_vm(self, vm):
        """Test that LA loads the correct address when executed"""
        program = """
.data
test_value: .word 0xDEADBEEF

.text
    LA x10, test_value
    LW x11, 0(x10)
    HALT
"""
        vm.load_program(program)
        vm.run()
        
        # x10 should contain the address of test_value (0x10000)
        assert vm.cpu.registers[10] == 0x10000
        
        # x11 should contain the value loaded from that address
        assert vm.cpu.registers[11] == 0xDEADBEEF
    
    def test_la_with_string_loading(self, vm):
        """Test LA for loading string addresses"""
        program = """
.data
msg: .string "Test"

.text
    LA a0, msg
    LBU a1, 0(a0)  # Load first character 'T'
    LBU a2, 1(a0)  # Load second character 'e'
    HALT
"""
        vm.load_program(program)
        vm.run()
        
        # a0 should have address of msg
        assert vm.cpu.registers[10] == 0x10000
        
        # a1 should have 'T' (0x54)
        assert vm.cpu.registers[11] == ord('T')
        
        # a2 should have 'e' (0x65)
        assert vm.cpu.registers[12] == ord('e')
    
    def test_la_multiple_data_labels(self, vm):
        """Test LA with multiple data labels"""
        program = """
.data
num1: .word 10
num2: .word 20
num3: .word 30

.text
    LA t0, num1
    LA t1, num2
    LA t2, num3
    
    LW a0, 0(t0)
    LW a1, 0(t1)
    LW a2, 0(t2)
    
    HALT
"""
        vm.load_program(program)
        vm.run()
        
        # Check addresses are loaded correctly
        assert vm.cpu.registers[5] == 0x10000  # t0 = num1
        assert vm.cpu.registers[6] == 0x10004  # t1 = num2
        assert vm.cpu.registers[7] == 0x10008  # t2 = num3
        
        # Check values are loaded correctly
        assert vm.cpu.registers[10] == 10  # a0
        assert vm.cpu.registers[11] == 20  # a1
        assert vm.cpu.registers[12] == 30  # a2
    
    def test_la_for_function_pointers(self, vm):
        """Test LA for loading function addresses (function pointers)"""
        program = """
.text
main:
    LA t0, add_five
    JALR ra, t0, 0
    HALT

add_five:
    ADDI a0, a0, 5
    JALR zero, ra, 0
"""
        vm.load_program(program)
        vm.cpu.registers[10] = 10  # a0 = 10
        vm.run()
        
        # a0 should be incremented by 5
        assert vm.cpu.registers[10] == 15
    
    def test_la_with_mixed_sections(self, vm):
        """Test LA works correctly with both text and data labels"""
        program = """
.data
value: .word 42

.text
    LA a0, value
    LA a1, function
    LW a2, 0(a0)
    HALT

function:
    ADDI a3, a3, 1
    JALR zero, ra, 0
"""
        vm.load_program(program)
        vm.run()
        
        # a0 should have data address
        assert vm.cpu.registers[10] == 0x10000
        
        # a1 should have function address (after LA expansion + LW + HALT)
        # LA a0 -> 2 instructions (0, 4)
        # LA a1 -> 2 instructions (8, 12)
        # LW -> 1 instruction (16)
        # HALT -> 1 instruction (20)
        # function starts at 24
        assert vm.cpu.registers[11] == 24
        
        # a2 should have the value 42
        assert vm.cpu.registers[12] == 42


class TestLAEdgeCases:
    """Test edge cases and boundary conditions for LA"""
    
    def test_la_with_zero_address(self, vm):
        """Test LA with address 0x00000 (text section start)"""
        program = """
.text
start:
    LA x10, start
    HALT
"""
        vm.load_program(program)
        vm.run()
        
        # x10 should be 0 (start of program)
        assert vm.cpu.registers[10] == 0
    
    def test_la_case_insensitive(self, assembler):
        """Test that LA is case insensitive"""
        program = """
.data
test: .word 123

.text
    la x5, test
    La x6, test
    LA x7, test
"""
        instructions = assembler.assemble(program)
        
        # Should produce 6 instructions (3 LA * 2)
        assert len(instructions) == 6
        
        # All should be LUI, ADDI, LUI, ADDI, LUI, ADDI
        assert instructions[0].opcode == "LUI"
        assert instructions[1].opcode == "ADDI"
        assert instructions[2].opcode == "LUI"
        assert instructions[3].opcode == "ADDI"
        assert instructions[4].opcode == "LUI"
        assert instructions[5].opcode == "ADDI"
    
    def test_la_all_registers(self, assembler):
        """Test LA with various register types"""
        program = """
.data
data: .word 1

.text
    LA zero, data    # x0 (though this is pointless)
    LA ra, data      # x1
    LA sp, data      # x2
    LA t0, data      # x5
    LA s0, data      # x8
    LA a0, data      # x10
"""
        instructions = assembler.assemble(program)
        
        # Should produce 12 instructions (6 LA * 2)
        assert len(instructions) == 12
        
        # Check register assignments
        assert instructions[0].rd == 0   # zero
        assert instructions[2].rd == 1   # ra
        assert instructions[4].rd == 2   # sp
        assert instructions[6].rd == 5   # t0
        assert instructions[8].rd == 8   # s0
        assert instructions[10].rd == 10 # a0
