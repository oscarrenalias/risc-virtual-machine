"""
Display module for the RISC VM
Provides text-mode display with 80x25 character grid
"""

import sys

class Display:
    """
    Text-mode display with memory-mapped I/O
    - 80 columns × 25 rows
    - ASCII character support
    - Cursor positioning
    - Auto-scrolling
    """
    
    COLS = 80
    ROWS = 25
    PAGES = 16
    
    def __init__(self):
        """Initialize the display"""
        self.buffer = [[' ' for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.cursor_x = 0
        self.cursor_y = 0
        self.current_page = 0
        self.mode = 0  # 0 = text mode
        self.auto_scroll = True
        self.dirty = True  # Track if display needs redrawing
    
    def write_char(self, x, y, char):
        """
        Write a character at position (x, y)
        
        Args:
            x: Column position (0-79)
            y: Row position (0-24)
            char: ASCII character code (0-127)
        """
        if 0 <= x < self.COLS and 0 <= y < self.ROWS:
            # Handle special characters
            if char == 0x0A:  # Newline
                self.cursor_y += 1
                self.cursor_x = 0
            elif char == 0x0D:  # Carriage return
                self.cursor_x = 0
            elif char == 0x08:  # Backspace
                if self.cursor_x > 0:
                    self.cursor_x -= 1
                    self.buffer[self.cursor_y][self.cursor_x] = ' '
            elif char == 0x09:  # Tab
                spaces = 4 - (self.cursor_x % 4)
                for _ in range(spaces):
                    if self.cursor_x < self.COLS:
                        self.buffer[self.cursor_y][self.cursor_x] = ' '
                        self.cursor_x += 1
            elif 32 <= char <= 126:  # Printable ASCII
                self.buffer[y][x] = chr(char)
                self.dirty = True
    
    def write_at_cursor(self, char):
        """
        Write a character at the current cursor position and advance cursor
        
        Args:
            char: ASCII character code
        """
        if char == 0x0A:  # Newline
            self.cursor_y += 1
            self.cursor_x = 0
        elif char == 0x0D:  # Carriage return
            self.cursor_x = 0
        elif char == 0x08:  # Backspace
            if self.cursor_x > 0:
                self.cursor_x -= 1
                self.buffer[self.cursor_y][self.cursor_x] = ' '
        elif char == 0x09:  # Tab
            spaces = 4 - (self.cursor_x % 4)
            for _ in range(spaces):
                if self.cursor_x < self.COLS:
                    self.buffer[self.cursor_y][self.cursor_x] = ' '
                    self.cursor_x += 1
        elif 32 <= char <= 126:  # Printable ASCII
            self.buffer[self.cursor_y][self.cursor_x] = chr(char)
            self.cursor_x += 1
            
            # Wrap to next line
            if self.cursor_x >= self.COLS:
                self.cursor_x = 0
                self.cursor_y += 1
        
        # Handle scrolling
        if self.cursor_y >= self.ROWS:
            if self.auto_scroll:
                self.scroll_up()
            else:
                self.cursor_y = self.ROWS - 1
        
        self.dirty = True
    
    def scroll_up(self):
        """Scroll the display up by one line"""
        # Move all rows up
        self.buffer = self.buffer[1:] + [[' ' for _ in range(self.COLS)]]
        self.cursor_y = self.ROWS - 1
        self.dirty = True
    
    def clear(self):
        """Clear the entire display"""
        self.buffer = [[' ' for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.cursor_x = 0
        self.cursor_y = 0
        self.dirty = True
    
    def set_cursor(self, x, y):
        """Set cursor position"""
        if 0 <= x < self.COLS:
            self.cursor_x = x
        if 0 <= y < self.ROWS:
            self.cursor_y = y
    
    def render(self, show_cursor=False):
        """
        Render the display to the terminal
        
        Args:
            show_cursor: If True, show cursor position
        """
        if not self.dirty:
            return
        
        # Clear terminal and move to home
        print('\033[2J\033[H', end='')
        
        # Draw top border
        print('┌' + '─' * self.COLS + '┐')
        
        # Draw buffer with side borders
        for y, row in enumerate(self.buffer):
            line = ''.join(row)
            
            # Highlight cursor position if enabled
            if show_cursor and y == self.cursor_y:
                line = (line[:self.cursor_x] + 
                       '\033[7m' + line[self.cursor_x] + '\033[0m' + 
                       line[self.cursor_x+1:])
            
            print('│' + line + '│')
        
        # Draw bottom border
        print('└' + '─' * self.COLS + '┘')
        
        # Show cursor position
        if show_cursor:
            print(f'Cursor: ({self.cursor_x}, {self.cursor_y})', end='')
        
        sys.stdout.flush()
        self.dirty = False
    
    def render_simple(self):
        """Render without borders (simpler output)"""
        if not self.dirty:
            return
        
        print('\033[2J\033[H', end='')  # Clear and home
        for row in self.buffer:
            print(''.join(row))
        sys.stdout.flush()
        self.dirty = False
    
    def get_text(self):
        """Get the entire display buffer as a string"""
        return '\n'.join(''.join(row) for row in self.buffer)
    
    def get_line(self, y):
        """Get a specific line from the display"""
        if 0 <= y < self.ROWS:
            return ''.join(self.buffer[y])
        return ''
