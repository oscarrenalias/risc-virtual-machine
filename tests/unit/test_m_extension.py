"""
Unit tests for M-extension (Multiply/Divide) instructions
Tests MUL, DIV, DIVU, REM, REMU with various edge cases
"""

import pytest


# Using vm fixture from conftest.py - no need for custom fixture


class TestMUL:
    """Test MUL instruction - multiply (lower 32 bits)"""
    
    def test_mul_positive_numbers(self, vm):
        """Test multiplication of positive numbers"""
        program = """
        ADDI x1, x0, 5
        ADDI x2, x0, 7
        MUL x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 35
    
    def test_mul_negative_numbers(self, vm):
        """Test multiplication with negative numbers"""
        program = """
        ADDI x1, x0, -5
        ADDI x2, x0, 7
        MUL x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        result = vm.cpu.to_signed(vm.cpu.read_register(3))
        assert result == -35
    
    def test_mul_both_negative(self, vm):
        """Test multiplication of two negative numbers"""
        program = """
        ADDI x1, x0, -5
        ADDI x2, x0, -7
        MUL x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 35
    
    def test_mul_by_zero(self, vm):
        """Test multiplication by zero"""
        program = """
        ADDI x1, x0, 42
        ADDI x2, x0, 0
        MUL x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 0
    
    def test_mul_large_numbers(self, vm):
        """Test multiplication of large numbers (tests lower 32 bits)"""
        program = """
        LUI x1, 0x10000
        ADDI x1, x1, 0
        LUI x2, 0x10000
        ADDI x2, x2, 0
        MUL x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        # 0x10000000 * 0x10000000 = 0x100000000000000 (only lower 32 bits = 0)
        assert vm.cpu.read_register(3) == 0
    
    def test_mul_overflow(self, vm):
        """Test multiplication overflow returns lower 32 bits"""
        program = """
        # Load 0x7FFFFFFF (max signed int)
        LUI x1, 0x80000
        ADDI x1, x1, -1
        ADDI x2, x0, 2
        MUL x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        # Result should wrap around
        result = vm.cpu.read_register(3)
        assert result == 0xFFFFFFFE  # 2147483647 * 2 = 4294967294 (lower 32 bits)


class TestDIV:
    """Test DIV instruction - signed division"""
    
    def test_div_positive_numbers(self, vm):
        """Test division of positive numbers"""
        program = """
        ADDI x1, x0, 20
        ADDI x2, x0, 4
        DIV x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 5
    
    def test_div_with_remainder(self, vm):
        """Test division with remainder (should truncate)"""
        program = """
        ADDI x1, x0, 23
        ADDI x2, x0, 4
        DIV x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 5
    
    def test_div_negative_dividend(self, vm):
        """Test division with negative dividend"""
        program = """
        ADDI x1, x0, -20
        ADDI x2, x0, 4
        DIV x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        result = vm.cpu.to_signed(vm.cpu.read_register(3))
        assert result == -5
    
    def test_div_negative_divisor(self, vm):
        """Test division with negative divisor"""
        program = """
        ADDI x1, x0, 20
        ADDI x2, x0, -4
        DIV x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        result = vm.cpu.to_signed(vm.cpu.read_register(3))
        assert result == -5
    
    def test_div_both_negative(self, vm):
        """Test division with both negative"""
        program = """
        ADDI x1, x0, -20
        ADDI x2, x0, -4
        DIV x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 5
    
    def test_div_by_zero(self, vm):
        """Test division by zero returns -1"""
        program = """
        ADDI x1, x0, 42
        ADDI x2, x0, 0
        DIV x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 0xFFFFFFFF
    
    def test_div_overflow_case(self, vm):
        """Test overflow case: -2^31 / -1"""
        program = """
        LUI x1, 0x80000
        ADDI x2, x0, -1
        DIV x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        # Should return -2^31 (the dividend)
        assert vm.cpu.read_register(3) == 0x80000000
    
    def test_div_rounds_toward_zero(self, vm):
        """Test that division rounds toward zero"""
        program = """
        ADDI x1, x0, -7
        ADDI x2, x0, 2
        DIV x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        result = vm.cpu.to_signed(vm.cpu.read_register(3))
        assert result == -3  # Rounds toward zero, not -4


class TestDIVU:
    """Test DIVU instruction - unsigned division"""
    
    def test_divu_positive_numbers(self, vm):
        """Test unsigned division of positive numbers"""
        program = """
        ADDI x1, x0, 20
        ADDI x2, x0, 4
        DIVU x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 5
    
    def test_divu_large_numbers(self, vm):
        """Test unsigned division treats values as unsigned"""
        program = """
        # Load 0xFFFFFFFF (-1 as unsigned = 4294967295)
        ADDI x1, x0, -1
        ADDI x2, x0, 2
        DIVU x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        # 0xFFFFFFFF / 2 = 0x7FFFFFFF (unsigned: 4294967295 / 2 = 2147483647)
        assert vm.cpu.read_register(3) == 0x7FFFFFFF
    
    def test_divu_by_zero(self, vm):
        """Test unsigned division by zero returns 2^32-1"""
        program = """
        ADDI x1, x0, 42
        ADDI x2, x0, 0
        DIVU x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 0xFFFFFFFF


class TestREM:
    """Test REM instruction - signed remainder"""
    
    def test_rem_positive_numbers(self, vm):
        """Test remainder of positive numbers"""
        program = """
        ADDI x1, x0, 23
        ADDI x2, x0, 5
        REM x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 3
    
    def test_rem_negative_dividend(self, vm):
        """Test remainder with negative dividend"""
        program = """
        ADDI x1, x0, -23
        ADDI x2, x0, 5
        REM x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        result = vm.cpu.to_signed(vm.cpu.read_register(3))
        assert result == -3  # Sign matches dividend
    
    def test_rem_negative_divisor(self, vm):
        """Test remainder with negative divisor"""
        program = """
        ADDI x1, x0, 23
        ADDI x2, x0, -5
        REM x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 3  # Sign matches dividend
    
    def test_rem_both_negative(self, vm):
        """Test remainder with both negative"""
        program = """
        ADDI x1, x0, -23
        ADDI x2, x0, -5
        REM x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        result = vm.cpu.to_signed(vm.cpu.read_register(3))
        assert result == -3  # Sign matches dividend
    
    def test_rem_by_zero(self, vm):
        """Test remainder by zero returns dividend"""
        program = """
        ADDI x1, x0, 42
        ADDI x2, x0, 0
        REM x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 42
    
    def test_rem_overflow_case(self, vm):
        """Test overflow case: -2^31 % -1 returns 0"""
        program = """
        LUI x1, 0x80000
        ADDI x2, x0, -1
        REM x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 0
    
    def test_rem_exact_division(self, vm):
        """Test remainder when division is exact"""
        program = """
        ADDI x1, x0, 20
        ADDI x2, x0, 4
        REM x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 0


class TestREMU:
    """Test REMU instruction - unsigned remainder"""
    
    def test_remu_positive_numbers(self, vm):
        """Test unsigned remainder of positive numbers"""
        program = """
        ADDI x1, x0, 23
        ADDI x2, x0, 5
        REMU x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 3
    
    def test_remu_large_numbers(self, vm):
        """Test unsigned remainder treats values as unsigned"""
        program = """
        # Load 0xFFFFFFFF (-1 as unsigned = 4294967295)
        ADDI x1, x0, -1
        ADDI x2, x0, 10
        REMU x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        # 0xFFFFFFFF % 10 = 4294967295 % 10 = 5
        assert vm.cpu.read_register(3) == 5
    
    def test_remu_by_zero(self, vm):
        """Test unsigned remainder by zero returns dividend"""
        program = """
        ADDI x1, x0, 42
        ADDI x2, x0, 0
        REMU x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 42
    
    def test_remu_exact_division(self, vm):
        """Test unsigned remainder when division is exact"""
        program = """
        ADDI x1, x0, 20
        ADDI x2, x0, 4
        REMU x3, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(3) == 0


class TestMExtensionCombinations:
    """Test combinations of M-extension instructions"""
    
    def test_mul_div_roundtrip(self, vm):
        """Test multiply then divide returns original"""
        program = """
        ADDI x1, x0, 7
        ADDI x2, x0, 5
        MUL x3, x1, x2
        DIV x4, x3, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(4) == 7
    
    def test_div_rem_combination(self, vm):
        """Test quotient and remainder together"""
        program = """
        ADDI x1, x0, 23
        ADDI x2, x0, 5
        DIV x3, x1, x2
        REM x4, x1, x2
        HALT
        """
        vm.load_program(program)
        vm.run()
        quotient = vm.cpu.read_register(3)
        remainder = vm.cpu.read_register(4)
        assert quotient == 4
        assert remainder == 3
        # Verify: dividend = quotient * divisor + remainder
        assert 23 == quotient * 5 + remainder
    
    def test_factorial_using_mul(self, vm):
        """Test factorial calculation using MUL"""
        program = """
        ADDI x1, x0, 5        # n = 5
        ADDI x2, x0, 1        # result = 1
        ADDI x3, x0, 1        # i = 1
    loop:
        BLT x1, x3, done      # if i > n, done
        MUL x2, x2, x3        # result *= i
        ADDI x3, x3, 1        # i++
        JAL x0, loop
    done:
        HALT
        """
        vm.load_program(program)
        vm.run()
        assert vm.cpu.read_register(2) == 120  # 5! = 120
