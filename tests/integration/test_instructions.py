"""
Integration tests for VM instruction execution
Tests individual instructions executing through the full VM
"""

import pytest
from tests.fixtures.test_helpers import run_and_get_register, run_program_until_halt


class TestArithmeticInstructions:
    """Test arithmetic instructions execute correctly"""
    
    def test_add_basic(self, vm):
        """Test ADD instruction"""
        program = """
        ADDI x1, x0, 10
        ADDI x2, x0, 20
        ADD x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 30
        
    def test_add_overflow(self, vm):
        """Test ADD with overflow wraps to 32-bit"""
        program = """
        LUI x1, 0xFFFFF      # x1 = 0xFFFFF000
        ADDI x1, x1, 0x7FF   # x1 = 0xFFFFF7FF  
        ADDI x1, x1, 0x7FF   # x1 = 0xFFFFFFFF - 1 (needs 2 adds due to imm limit)
        ADDI x1, x1, 1       # x1 = 0xFFFFFFFF
        ADDI x2, x0, 2
        ADD x3, x1, x2       # Should wrap around
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        # Result should wrap: 0xFFFFFFFF + 2 = 0x00000001
        assert result == 1
        
    def test_sub_basic(self, vm):
        """Test SUB instruction"""
        program = """
        ADDI x1, x0, 50
        ADDI x2, x0, 20
        SUB x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 30
        
    def test_sub_negative_result(self, vm):
        """Test SUB producing negative result"""
        program = """
        ADDI x1, x0, 10
        ADDI x2, x0, 20
        SUB x3, x1, x2       # 10 - 20 = -10 (0xFFFFFFF6 unsigned)
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 0xFFFFFFF6


class TestLogicalInstructions:
    """Test logical operations"""
    
    def test_and_instruction(self, vm):
        """Test AND instruction"""
        program = """
        ADDI x1, x0, 0xFF
        ADDI x2, x0, 0xF0
        AND x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 0xF0
        
    def test_or_instruction(self, vm):
        """Test OR instruction"""
        program = """
        ADDI x1, x0, 0x0F
        ADDI x2, x0, 0xF0
        OR x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 0xFF
        
    def test_xor_instruction(self, vm):
        """Test XOR instruction"""
        program = """
        ADDI x1, x0, 0xFF
        ADDI x2, x0, 0x0F
        XOR x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 0xF0


class TestShiftInstructions:
    """Test shift operations"""
    
    def test_sll_shift_left(self, vm):
        """Test SLL (shift left logical)"""
        program = """
        ADDI x1, x0, 1
        ADDI x2, x0, 4
        SLL x3, x1, x2       # 1 << 4 = 16
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 16
        
    def test_srl_shift_right(self, vm):
        """Test SRL (shift right logical)"""
        program = """
        ADDI x1, x0, 64
        ADDI x2, x0, 2
        SRL x3, x1, x2       # 64 >> 2 = 16
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 16
        
    def test_sra_arithmetic_shift(self, vm):
        """Test SRA (shift right arithmetic) with sign extension"""
        program = """
        ADDI x1, x0, -8      # 0xFFFFFFF8
        ADDI x2, x0, 1
        SRA x3, x1, x2       # Arithmetic shift preserves sign
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 0xFFFFFFFC  # -4 in two's complement


class TestComparisonInstructions:
    """Test comparison instructions"""
    
    def test_slt_less_than_signed(self, vm):
        """Test SLT (set less than, signed)"""
        program = """
        ADDI x1, x0, -5
        ADDI x2, x0, 10
        SLT x3, x1, x2       # -5 < 10 (signed) -> 1
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 1
        
    def test_sltu_less_than_unsigned(self, vm):
        """Test SLTU (set less than, unsigned)"""
        program = """
        ADDI x1, x0, -5      # 0xFFFFFFFB (unsigned)
        ADDI x2, x0, 10
        SLTU x3, x1, x2      # Large unsigned < 10 -> 0
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 0


class TestMemoryInstructions:
    """Test load/store instructions"""
    
    def test_store_and_load_word(self, vm):
        """Test SW and LW instructions"""
        program = """
        ADDI x1, x0, 42
        ADDI x2, x0, 0x1000
        SW x1, 0(x2)         # Store 42 at 0x1000
        LW x3, 0(x2)         # Load back from 0x1000
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 42
        
    def test_load_with_offset(self, vm):
        """Test load with offset"""
        program = """
        ADDI x1, x0, 100
        ADDI x2, x0, 0x2000
        SW x1, 8(x2)         # Store at 0x2008
        LW x3, 8(x2)         # Load from 0x2008
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 100
        
    def test_byte_operations(self, vm):
        """Test byte load/store"""
        program = """
        ADDI x1, x0, 0xFF
        ADDI x2, x0, 0x3000
        SB x1, 0(x2)         # Store byte
        LBU x3, 0(x2)        # Load byte unsigned
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 0xFF


class TestBranchInstructions:
    """Test branch instructions"""
    
    def test_beq_branch_taken(self, vm):
        """Test BEQ branch taken"""
        program = """
        ADDI x1, x0, 10
        ADDI x2, x0, 10
        BEQ x1, x2, skip     # Branch taken
        ADDI x3, x0, 99      # Skipped
    skip:
        ADDI x3, x0, 42      # Executed
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 42
        
    def test_beq_branch_not_taken(self, vm):
        """Test BEQ branch not taken"""
        program = """
        ADDI x1, x0, 10
        ADDI x2, x0, 20
        BEQ x1, x2, skip     # Branch not taken
        ADDI x3, x0, 99      # Executed
    skip:
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 99
        
    def test_bne_branch(self, vm):
        """Test BNE (branch not equal)"""
        program = """
        ADDI x1, x0, 10
        ADDI x2, x0, 20
        BNE x1, x2, target   # Branch taken (not equal)
        ADDI x3, x0, 99      # Skipped
    target:
        ADDI x3, x0, 42      # Executed
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 42
        
    def test_blt_branch_less_than(self, vm):
        """Test BLT (branch less than)"""
        program = """
        ADDI x1, x0, 5
        ADDI x2, x0, 10
        BLT x1, x2, target   # 5 < 10, branch taken
        ADDI x3, x0, 99      # Skipped
    target:
        ADDI x3, x0, 42      # Executed
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 42


class TestJumpInstructions:
    """Test jump instructions"""
    
    def test_jal_jump_and_link(self, vm):
        """Test JAL saves return address"""
        program = """
        JAL x1, target       # Jump and save return address
        ADDI x3, x0, 99      # Skipped
    target:
        ADDI x3, x0, 42      # Executed
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 42
        # x1 should contain return address (PC+4 of JAL)
        return_addr = vm.cpu.read_register(1)
        assert return_addr == 4  # Address of ADDI after JAL
        
    def test_jalr_indirect_jump(self, vm):
        """Test JALR (jump and link register)"""
        program = """
        JAL x0, start        # Skip past target code
    target:
        ADDI x3, x0, 42      # Target code
        HALT
    start:
        ADDI x2, x0, 4       # Target address (instruction 1, offset 4)
        JALR x1, x2, 0       # Jump to address in x2
        ADDI x3, x0, 99      # Should be skipped
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 42


class TestLUIInstruction:
    """Test LUI (Load Upper Immediate)"""
    
    def test_lui_basic(self, vm):
        """Test LUI loads upper 20 bits"""
        program = """
        LUI x1, 0x12345
        HALT
        """
        result = run_and_get_register(vm, program, 1)
        # LUI loads bits [31:12], so 0x12345 << 12
        assert result == 0x12345000
        
    def test_lui_with_addi(self, vm):
        """Test LUI combined with ADDI for full 32-bit value"""
        program = """
        LUI x1, 0x12345
        ADDI x1, x1, 0x678
        HALT
        """
        result = run_and_get_register(vm, program, 1)
        assert result == 0x12345678


class TestLoopConstruct:
    """Test simple loop patterns"""
    
    def test_simple_counting_loop(self, vm):
        """Test loop that counts to 10"""
        program = """
        ADDI x1, x0, 0       # Counter
        ADDI x2, x0, 10      # Limit
    loop:
        ADDI x1, x1, 1       # Increment counter
        BLT x1, x2, loop     # Loop while counter < limit
        HALT
        """
        result = run_and_get_register(vm, program, 1)
        assert result == 10
        
    def test_accumulator_loop(self, vm):
        """Test loop with accumulation (sum 1+2+3+4+5)"""
        program = """
        ADDI x1, x0, 0       # Sum accumulator
        ADDI x2, x0, 1       # Current number
        ADDI x3, x0, 6       # Limit (one past last)
    loop:
        ADD x1, x1, x2       # Add current to sum
        ADDI x2, x2, 1       # Increment current
        BLT x2, x3, loop     # Continue if current < limit
        HALT
        """
        result = run_and_get_register(vm, program, 1)
        assert result == 15  # 1+2+3+4+5 = 15


class TestMultiplyDivideInstructions:
    """Test M-extension multiply and divide instructions"""
    
    def test_mul_basic(self, vm):
        """Test MUL instruction basic multiplication"""
        program = """
        ADDI x1, x0, 6
        ADDI x2, x0, 7
        MUL x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 42
    
    def test_mul_negative(self, vm):
        """Test MUL with negative numbers"""
        program = """
        ADDI x1, x0, -6
        ADDI x2, x0, 7
        MUL x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert vm.cpu.to_signed(result) == -42
    
    def test_div_basic(self, vm):
        """Test DIV instruction basic division"""
        program = """
        ADDI x1, x0, 42
        ADDI x2, x0, 7
        DIV x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 6
    
    def test_div_by_zero(self, vm):
        """Test DIV by zero returns -1"""
        program = """
        ADDI x1, x0, 42
        ADDI x2, x0, 0
        DIV x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 0xFFFFFFFF
    
    def test_divu_basic(self, vm):
        """Test DIVU instruction unsigned division"""
        program = """
        ADDI x1, x0, 42
        ADDI x2, x0, 7
        DIVU x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 6
    
    def test_divu_by_zero(self, vm):
        """Test DIVU by zero returns 2^32-1"""
        program = """
        ADDI x1, x0, 42
        ADDI x2, x0, 0
        DIVU x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 0xFFFFFFFF
    
    def test_rem_basic(self, vm):
        """Test REM instruction basic remainder"""
        program = """
        ADDI x1, x0, 23
        ADDI x2, x0, 5
        REM x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 3
    
    def test_rem_negative(self, vm):
        """Test REM with negative dividend"""
        program = """
        ADDI x1, x0, -23
        ADDI x2, x0, 5
        REM x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert vm.cpu.to_signed(result) == -3
    
    def test_remu_basic(self, vm):
        """Test REMU instruction unsigned remainder"""
        program = """
        ADDI x1, x0, 23
        ADDI x2, x0, 5
        REMU x3, x1, x2
        HALT
        """
        result = run_and_get_register(vm, program, 3)
        assert result == 3
    
    def test_div_rem_combination(self, vm):
        """Test DIV and REM together verify dividend = quotient*divisor + remainder"""
        program = """
        ADDI x1, x0, 23       # dividend
        ADDI x2, x0, 5        # divisor
        DIV x3, x1, x2        # quotient
        REM x4, x1, x2        # remainder
        HALT
        """
        run_program_until_halt(vm, program)
        quotient = vm.cpu.read_register(3)
        remainder = vm.cpu.read_register(4)
        assert quotient == 4
        assert remainder == 3
        # Verify formula
        assert 23 == quotient * 5 + remainder

