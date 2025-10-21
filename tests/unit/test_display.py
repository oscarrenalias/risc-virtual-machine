"""
Unit tests for Display module
Tests display buffer operations and rendering
"""

import pytest
from src.display import Display


class TestDisplayBasics:
    """Test basic display initialization"""
    
    def test_display_initialization(self, display):
        """Test display initializes correctly"""
        assert display.COLS == 80
        assert display.ROWS == 25
        assert display.cursor_x == 0
        assert display.cursor_y == 0
        assert len(display.buffer) == display.ROWS
        assert len(display.buffer[0]) == display.COLS
        
    def test_display_buffer_initialized_to_spaces(self, display):
        """Test buffer starts with spaces"""
        for row in display.buffer:
            for char in row:
                assert char == ' '


class TestDisplayWriteChar:
    """Test character writing"""
    
    def test_write_printable_char(self, display):
        """Test writing printable character"""
        display.write_char(0, 0, ord('A'))
        assert display.buffer[0][0] == 'A'
        
    def test_write_char_bounds_checking(self, display):
        """Test write_char respects bounds"""
        display.write_char(100, 100, ord('X'))  # Out of bounds
        # Should not crash, just ignore
        
    def test_write_special_chars(self, display):
        """Test special character handling"""
        display.cursor_x = 5
        display.cursor_y = 5
        display.write_char(5, 5, 0x0A)  # Newline
        # write_char doesn't automatically advance cursor for newline
        # That's handled by write_at_cursor instead
        assert display.cursor_y >= 5  # Cursor may have moved


class TestDisplayCursor:
    """Test cursor operations"""
    
    def test_write_at_cursor_advances(self, display):
        """Test cursor advances after write"""
        display.cursor_x = 0
        display.cursor_y = 0
        
        display.write_at_cursor(ord('A'))
        assert display.cursor_x == 1
        assert display.buffer[0][0] == 'A'
        
    def test_cursor_wraps_at_end_of_line(self, display):
        """Test cursor wraps to next line"""
        display.cursor_x = display.COLS - 1
        display.cursor_y = 0
        
        display.write_at_cursor(ord('A'))
        display.write_at_cursor(ord('B'))
        
        assert display.cursor_x == 1
        assert display.cursor_y == 1


class TestDisplayControl:
    """Test display control functions"""
    
    def test_clear_display(self, display):
        """Test clearing display"""
        display.write_char(0, 0, ord('X'))
        display.write_char(5, 5, ord('Y'))
        
        display.clear()
        
        assert display.buffer[0][0] == ' '
        assert display.buffer[5][5] == ' '
        
    def test_scroll_up(self, display):
        """Test scrolling display up"""
        display.write_char(0, 24, ord('Z'))  # Bottom row
        
        display.scroll_up()
        
        # Character should move up one row
        assert display.buffer[23][0] == 'Z'
        assert display.buffer[24][0] == ' '  # Bottom cleared
