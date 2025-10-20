"""
CPU module for the RISC VM
Implements 32-bit RISC processor with 32 general-purpose registers
"""

class CPU:
    """
    32-bit RISC CPU with:
    - 32 general-purpose registers (x0-x31)
    - Program counter (PC)
    - x0 is hardwired to zero
    """
    
    NUM_REGISTERS = 32
    
    def __init__(self):
        """Initialize CPU with registers and PC"""
        self.registers = [0] * self.NUM_REGISTERS
        self.pc = 0  # Program counter
        self.halted = False
        self.instruction_count = 0
    
    def read_register(self, reg):
        """
        Read a register value
        
        Args:
            reg: Register number (0-31) or name (x0-x31)
            
        Returns:
            32-bit register value
        """
        reg_num = self._parse_register(reg)
        if 0 <= reg_num < self.NUM_REGISTERS:
            return self.registers[reg_num]
        raise ValueError(f"Invalid register: {reg}")
    
    def write_register(self, reg, value):
        """
        Write a value to a register
        
        Args:
            reg: Register number (0-31) or name (x0-x31)
            value: 32-bit value to write
        """
        reg_num = self._parse_register(reg)
        
        if reg_num < 0 or reg_num >= self.NUM_REGISTERS:
            raise ValueError(f"Invalid register: {reg}")
        
        # x0 is hardwired to zero
        if reg_num == 0:
            return
        
        # Mask to 32 bits (ensure unsigned)
        self.registers[reg_num] = value & 0xFFFFFFFF
    
    def _parse_register(self, reg):
        """
        Parse register identifier to register number
        
        Args:
            reg: Register number (int) or name (str like 'x5')
            
        Returns:
            Register number (0-31)
        """
        if isinstance(reg, int):
            return reg
        
        if isinstance(reg, str):
            # Handle register names like 'x5' or 'X5'
            reg = reg.lower().strip()
            if reg.startswith('x'):
                try:
                    return int(reg[1:])
                except ValueError:
                    pass
            
            # Handle named registers
            aliases = {
                'zero': 0,
                'ra': 1,    # Return address
                'sp': 2,    # Stack pointer
                'gp': 3,    # Global pointer
                'tp': 4,    # Thread pointer
                'fp': 8,    # Frame pointer (alias for x8/s0)
                's0': 8,
            }
            if reg in aliases:
                return aliases[reg]
        
        raise ValueError(f"Invalid register identifier: {reg}")
    
    def increment_pc(self, amount=4):
        """Increment program counter (default: 4 bytes per instruction)"""
        self.pc += amount
    
    def set_pc(self, address):
        """Set program counter to specific address"""
        self.pc = address & 0xFFFFFFFF
    
    def halt(self):
        """Halt the CPU"""
        self.halted = True
    
    def reset(self):
        """Reset CPU to initial state"""
        self.registers = [0] * self.NUM_REGISTERS
        self.pc = 0
        self.halted = False
        self.instruction_count = 0
    
    def dump_registers(self):
        """Return a formatted string of all register values"""
        lines = []
        lines.append(f"PC: 0x{self.pc:08X}  Instructions: {self.instruction_count}")
        lines.append("-" * 70)
        
        # Print registers in 4 columns
        for i in range(0, self.NUM_REGISTERS, 4):
            reg_strs = []
            for j in range(4):
                reg_num = i + j
                if reg_num < self.NUM_REGISTERS:
                    name = self._get_register_name(reg_num)
                    value = self.registers[reg_num]
                    reg_strs.append(f"{name:4s}: 0x{value:08X}")
            lines.append("  ".join(reg_strs))
        
        return "\n".join(lines)
    
    def _get_register_name(self, reg_num):
        """Get conventional name for register"""
        names = {
            0: 'x0', 1: 'x1', 2: 'x2', 3: 'x3',
            4: 'x4', 5: 'x5', 6: 'x6', 7: 'x7',
            8: 'x8', 9: 'x9', 10: 'x10', 11: 'x11',
            12: 'x12', 13: 'x13', 14: 'x14', 15: 'x15',
            16: 'x16', 17: 'x17', 18: 'x18', 19: 'x19',
            20: 'x20', 21: 'x21', 22: 'x22', 23: 'x23',
            24: 'x24', 25: 'x25', 26: 'x26', 27: 'x27',
            28: 'x28', 29: 'x29', 30: 'x30', 31: 'x31',
        }
        return names.get(reg_num, f'x{reg_num}')
    
    def sign_extend(self, value, bits):
        """
        Sign-extend a value to 32 bits
        
        Args:
            value: The value to extend
            bits: Number of bits in the original value
            
        Returns:
            32-bit sign-extended value
        """
        sign_bit = 1 << (bits - 1)
        if value & sign_bit:
            # Negative number, extend with 1s
            mask = (1 << bits) - 1
            return (value & mask) | (~mask & 0xFFFFFFFF)
        else:
            # Positive number, just mask
            return value & ((1 << bits) - 1)
    
    def to_signed(self, value):
        """Convert 32-bit unsigned to signed integer"""
        if value & 0x80000000:
            return value - 0x100000000
        return value
    
    def to_unsigned(self, value):
        """Convert signed integer to 32-bit unsigned"""
        return value & 0xFFFFFFFF
