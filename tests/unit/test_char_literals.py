"""
Tests for character literal support in assembler
"""

import pytest
from src.assembler import Assembler, AssemblerError


class TestCharacterLiterals:
    """Test character literal preprocessing"""
    
    def test_simple_character(self):
        """Test simple character literal"""
        assembler = Assembler()
        source = """
        ADDI x1, x0, 'A'
        HALT
        """
        instructions = assembler.assemble(source)
        assert len(instructions) == 2
        assert instructions[0].imm == 65  # ASCII 'A'
    
    def test_lowercase_character(self):
        """Test lowercase character literal"""
        assembler = Assembler()
        source = """
        ADDI x1, x0, 'z'
        HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 122  # ASCII 'z'
    
    def test_digit_character(self):
        """Test digit character literal"""
        assembler = Assembler()
        source = """
        ADDI x1, x0, '0'
        HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 48  # ASCII '0'
    
    def test_space_character(self):
        """Test space character literal"""
        assembler = Assembler()
        source = """
        ADDI x1, x0, ' '
        HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 32  # ASCII space
    
    def test_special_characters(self):
        """Test various special characters"""
        assembler = Assembler()
        
        test_cases = [
            ('!', 33),
            ('@', 64),
            ('#', 35),
            ('$', 36),
            ('%', 37),
            ('^', 94),
            ('&', 38),
            ('*', 42),
            ('(', 40),
            (')', 41),
            ('-', 45),
            ('+', 43),
            ('=', 61),
            ('[', 91),
            (']', 93),
            ('{', 123),
            ('}', 125),
            (':', 58),
            (';', 59),
            (',', 44),
            ('.', 46),
            ('?', 63),
            ('/', 47),
            ('|', 124),
        ]
        
        for char, expected_value in test_cases:
            source = f"ADDI x1, x0, '{char}'\nHALT"
            instructions = assembler.assemble(source)
            assert instructions[0].imm == expected_value, f"Character '{char}' should be {expected_value}"
    
    def test_newline_escape(self):
        """Test newline escape sequence"""
        assembler = Assembler()
        source = r"""
        ADDI x1, x0, '\n'
        HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 10  # '\n' = 10
    
    def test_tab_escape(self):
        """Test tab escape sequence"""
        assembler = Assembler()
        source = r"""
        ADDI x1, x0, '\t'
        HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 9  # '\t' = 9
    
    def test_carriage_return_escape(self):
        """Test carriage return escape sequence"""
        assembler = Assembler()
        source = r"""
        ADDI x1, x0, '\r'
        HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 13  # '\r' = 13
    
    def test_null_escape(self):
        """Test null escape sequence"""
        assembler = Assembler()
        source = r"""
        ADDI x1, x0, '\0'
        HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 0  # '\0' = 0
    
    def test_single_quote_escape(self):
        """Test single quote escape sequence"""
        assembler = Assembler()
        source = r"""
        ADDI x1, x0, '\''
        HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 39  # '\'' = 39
    
    def test_backslash_escape(self):
        """Test backslash escape sequence"""
        assembler = Assembler()
        source = r"""
        ADDI x1, x0, '\\'
        HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 92  # '\\' = 92
    
    def test_multiple_char_literals_in_line(self):
        """Test multiple character literals in same program"""
        assembler = Assembler()
        source = """
        ADDI x1, x0, 'A'
        ADDI x2, x0, 'B'
        ADDI x3, x0, 'C'
        HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 65  # 'A'
        assert instructions[1].imm == 66  # 'B'
        assert instructions[2].imm == 67  # 'C'
    
    def test_char_literal_with_comment(self):
        """Test character literal with comment on same line"""
        assembler = Assembler()
        source = """
        ADDI x1, x0, 'X'  # Load character X
        HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 88  # 'X'
    
    def test_char_literal_in_branch(self):
        """Test character literal in branch comparison"""
        assembler = Assembler()
        source = """
        ADDI x1, x0, 'A'
        ADDI x2, x0, 'A'
        BEQ x1, x2, equal
        HALT
        equal:
            ADDI x3, x0, 1
            HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 65  # 'A'
        assert instructions[1].imm == 65  # 'A'
    
    def test_empty_char_literal_error(self):
        """Test that empty character literal raises error"""
        assembler = Assembler()
        source = """
        ADDI x1, x0, ''
        HALT
        """
        with pytest.raises(AssemblerError, match="Empty character literal"):
            assembler.assemble(source)
    
    def test_multi_char_literal_error(self):
        """Test that multi-character literal raises error"""
        assembler = Assembler()
        source = """
        ADDI x1, x0, 'AB'
        HALT
        """
        with pytest.raises(AssemblerError, match="Multi-character literal not supported"):
            assembler.assemble(source)
    
    def test_invalid_escape_sequence_error(self):
        """Test that invalid escape sequence raises error"""
        assembler = Assembler()
        source = r"""
        ADDI x1, x0, '\x'
        HALT
        """
        with pytest.raises(AssemblerError, match="Unknown escape sequence"):
            assembler.assemble(source)
    
    def test_char_literals_not_in_strings(self):
        """Test that character literals work properly (comments with quotes should be avoided)"""
        assembler = Assembler()
        source = """
        ADDI x1, x0, 'A'  # Load character A
        HALT
        """
        instructions = assembler.assemble(source)
        # Character literal is processed, then comment is removed
        assert instructions[0].imm == 65
    
    def test_numeric_and_char_mixed(self):
        """Test mixing numeric and character literals"""
        assembler = Assembler()
        source = """
        ADDI x1, x0, 42
        ADDI x2, x0, 'A'
        ADDI x3, x0, 0x2A
        HALT
        """
        instructions = assembler.assemble(source)
        assert instructions[0].imm == 42
        assert instructions[1].imm == 65  # 'A'
        assert instructions[2].imm == 42  # 0x2A
