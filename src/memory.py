"""
Memory module for the RISC VM
Provides 1MB of addressable memory with memory-mapped I/O for display
"""

class MemoryAccessError(Exception):
    """Raised when attempting to access invalid memory address"""
    pass

class MemoryProtectionError(Exception):
    """Raised when attempting to write to protected memory"""
    pass

class Memory:
    """
    1MB memory with the following layout:
    0x00000 - 0x0FFFF: Text segment (64KB)    - Program instructions
    0x10000 - 0x3FFFF: Data segment (192KB)   - Static/global data
    0x40000 - 0x7FFFF: Heap (256KB)           - Dynamic allocation
    0x80000 - 0xBFFFF: Stack (256KB)          - Grows downward from 0xBFFFF
    0xC0000 - 0xEFFFF: General RAM (192KB)    - Additional space
    0xF0000 - 0xFFFFF: Memory-mapped I/O (64KB)
    """
    
    # Memory region boundaries
    TEXT_START = 0x00000
    TEXT_END = 0x0FFFF
    DATA_START = 0x10000
    DATA_END = 0x3FFFF
    HEAP_START = 0x40000
    HEAP_END = 0x7FFFF
    STACK_START = 0xBFFFF  # Grows downward
    STACK_END = 0x80000
    RAM_START = 0xC0000
    RAM_END = 0xEFFFF
    MMIO_START = 0xF0000
    MMIO_END = 0xFFFFF
    
    # Display memory regions
    DISPLAY_BUFFER_START = 0xF0000
    DISPLAY_BUFFER_END = 0xF7CFF
    DISPLAY_CONTROL_START = 0xF7D00
    DISPLAY_CONTROL_END = 0xF7D7F
    
    # Display control register offsets
    CTRL_PAGE = 0xF7D00
    CTRL_CURSOR_X = 0xF7D01
    CTRL_CURSOR_Y = 0xF7D02
    CTRL_MODE = 0xF7D03
    CTRL_SCROLL = 0xF7D04
    CTRL_CLEAR = 0xF7D05
    
    SIZE = 1024 * 1024  # 1MB
    
    def __init__(self, display=None, protect_text=False):
        """
        Initialize memory
        
        Args:
            display: Display object for memory-mapped I/O
            protect_text: If True, prevent writes to text segment
        """
        self.data = bytearray(self.SIZE)
        self.display = display
        self.protect_text = protect_text
        
    def _check_bounds(self, address, size=4):
        """Check if address is within valid bounds"""
        if address < 0 or address + size > self.SIZE:
            raise MemoryAccessError(
                f"Memory access out of bounds: 0x{address:08X} (size: {size})"
            )
    
    def _check_alignment(self, address, alignment=4):
        """Check if address is properly aligned"""
        if address % alignment != 0:
            raise MemoryAccessError(
                f"Unaligned memory access: 0x{address:08X} (must be {alignment}-byte aligned)"
            )
    
    def read_byte(self, address):
        """Read a single byte from memory"""
        self._check_bounds(address, 1)
        return self.data[address]
    
    def write_byte(self, address, value):
        """Write a single byte to memory"""
        self._check_bounds(address, 1)
        
        # Check text segment protection
        if self.protect_text and self.TEXT_START <= address <= self.TEXT_END:
            raise MemoryProtectionError(
                f"Cannot write to protected text segment: 0x{address:08X}"
            )
        
        self.data[address] = value & 0xFF
    
    def read_word(self, address):
        """Read a 32-bit word from memory (little-endian)"""
        self._check_bounds(address, 4)
        self._check_alignment(address, 4)
        
        # Read 4 bytes in little-endian order
        value = int.from_bytes(self.data[address:address+4], byteorder='little', signed=False)
        return value
    
    def write_word(self, address, value):
        """Write a 32-bit word to memory (little-endian)"""
        self._check_bounds(address, 4)
        self._check_alignment(address, 4)
        
        # Check text segment protection
        if self.protect_text and self.TEXT_START <= address <= self.TEXT_END:
            raise MemoryProtectionError(
                f"Cannot write to protected text segment: 0x{address:08X}"
            )
        
        # Handle memory-mapped I/O
        if self.DISPLAY_BUFFER_START <= address <= self.DISPLAY_BUFFER_END:
            self._handle_display_write(address, value)
        elif self.DISPLAY_CONTROL_START <= address <= self.DISPLAY_CONTROL_END:
            self._handle_control_register_write(address, value)
        
        # Write 4 bytes in little-endian order
        value = value & 0xFFFFFFFF  # Ensure 32-bit value
        self.data[address:address+4] = value.to_bytes(4, byteorder='little', signed=False)
    
    def _handle_display_write(self, address, value):
        """Handle writes to display buffer"""
        if self.display is None:
            return
        
        # Calculate position in display buffer
        offset = address - self.DISPLAY_BUFFER_START
        
        # Each word can contain up to 4 characters
        for i in range(4):
            byte_val = (value >> (i * 8)) & 0xFF
            if byte_val != 0:  # Only write non-zero bytes
                char_offset = offset + i
                col = char_offset % self.display.COLS
                row = (char_offset // self.display.COLS) % self.display.ROWS
                self.display.write_char(col, row, byte_val)
    
    def _handle_control_register_write(self, address, value):
        """Handle writes to display control registers"""
        if self.display is None:
            return
        
        if address == self.CTRL_PAGE:
            self.display.current_page = value & 0x0F
        elif address == self.CTRL_CURSOR_X:
            self.display.cursor_x = value % self.display.COLS
        elif address == self.CTRL_CURSOR_Y:
            self.display.cursor_y = value % self.display.ROWS
        elif address == self.CTRL_MODE:
            self.display.mode = value
        elif address == self.CTRL_SCROLL:
            self.display.auto_scroll = bool(value)
        elif address == self.CTRL_CLEAR:
            self.display.clear()
    
    def load_program(self, program_bytes, start_address=TEXT_START):
        """Load a program into memory at the specified address"""
        if start_address + len(program_bytes) > self.SIZE:
            raise MemoryAccessError("Program too large for memory")
        
        self.data[start_address:start_address+len(program_bytes)] = program_bytes
    
    def dump(self, start_address, length=256):
        """Dump memory contents for debugging"""
        lines = []
        for i in range(0, length, 16):
            addr = start_address + i
            if addr >= self.SIZE:
                break
            
            # Hex bytes
            hex_bytes = ' '.join(f'{b:02X}' for b in self.data[addr:addr+16])
            
            # ASCII representation
            ascii_chars = ''.join(
                chr(b) if 32 <= b < 127 else '.'
                for b in self.data[addr:addr+16]
            )
            
            lines.append(f'0x{addr:08X}  {hex_bytes:<48}  {ascii_chars}')
        
        return '\n'.join(lines)
