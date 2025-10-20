"""
Instruction module for the RISC VM
Defines instruction formats and parsing
"""

from enum import Enum

class InstructionType(Enum):
    """Types of RISC instructions"""
    R_TYPE = 'R'  # Register-register operations (ADD, SUB, etc.)
    I_TYPE = 'I'  # Immediate operations (ADDI, LW, etc.)
    S_TYPE = 'S'  # Store operations (SW)
    B_TYPE = 'B'  # Branch operations (BEQ, BNE, etc.)
    J_TYPE = 'J'  # Jump operations (JAL, JALR)
    U_TYPE = 'U'  # Upper immediate (LUI)
    HALT = 'HALT'  # System halt

class Instruction:
    """Represents a parsed instruction"""
    
    def __init__(self, opcode, inst_type, rd=None, rs1=None, rs2=None, imm=None, label=None):
        """
        Initialize an instruction
        
        Args:
            opcode: Instruction mnemonic (e.g., 'ADD', 'LW')
            inst_type: InstructionType
            rd: Destination register
            rs1: Source register 1
            rs2: Source register 2
            imm: Immediate value
            label: Label for branches/jumps
        """
        self.opcode = opcode.upper()
        self.type = inst_type
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = imm
        self.label = label
    
    def __str__(self):
        """String representation of instruction"""
        parts = [self.opcode]
        
        if self.type == InstructionType.R_TYPE:
            parts.append(f"x{self.rd}, x{self.rs1}, x{self.rs2}")
        elif self.type == InstructionType.I_TYPE:
            if self.opcode in ['LW', 'LB', 'LH']:
                parts.append(f"x{self.rd}, {self.imm}(x{self.rs1})")
            else:
                parts.append(f"x{self.rd}, x{self.rs1}, {self.imm}")
        elif self.type == InstructionType.S_TYPE:
            parts.append(f"x{self.rs2}, {self.imm}(x{self.rs1})")
        elif self.type == InstructionType.B_TYPE:
            if self.label:
                parts.append(f"x{self.rs1}, x{self.rs2}, {self.label}")
            else:
                parts.append(f"x{self.rs1}, x{self.rs2}, {self.imm}")
        elif self.type == InstructionType.J_TYPE:
            if self.opcode == 'JAL':
                if self.label:
                    parts.append(f"x{self.rd}, {self.label}")
                else:
                    parts.append(f"x{self.rd}, {self.imm}")
            elif self.opcode == 'JALR':
                parts.append(f"x{self.rd}, x{self.rs1}, {self.imm}")
        elif self.type == InstructionType.U_TYPE:
            parts.append(f"x{self.rd}, {self.imm}")
        
        return ' '.join(parts)
    
    def __repr__(self):
        return f"Instruction({self.opcode}, {self.type.name})"

# Instruction set definitions
INSTRUCTION_SET = {
    # R-type instructions (register-register)
    'ADD': InstructionType.R_TYPE,
    'SUB': InstructionType.R_TYPE,
    'AND': InstructionType.R_TYPE,
    'OR': InstructionType.R_TYPE,
    'XOR': InstructionType.R_TYPE,
    'SLL': InstructionType.R_TYPE,  # Shift left logical
    'SRL': InstructionType.R_TYPE,  # Shift right logical
    'SRA': InstructionType.R_TYPE,  # Shift right arithmetic
    'SLT': InstructionType.R_TYPE,  # Set less than
    'SLTU': InstructionType.R_TYPE, # Set less than unsigned
    
    # I-type instructions (immediate)
    'ADDI': InstructionType.I_TYPE,
    'ANDI': InstructionType.I_TYPE,
    'ORI': InstructionType.I_TYPE,
    'XORI': InstructionType.I_TYPE,
    'SLLI': InstructionType.I_TYPE, # Shift left logical immediate
    'SRLI': InstructionType.I_TYPE, # Shift right logical immediate
    'SRAI': InstructionType.I_TYPE, # Shift right arithmetic immediate
    'SLTI': InstructionType.I_TYPE, # Set less than immediate
    'SLTIU': InstructionType.I_TYPE,# Set less than immediate unsigned
    
    # Load instructions (I-type)
    'LW': InstructionType.I_TYPE,   # Load word
    'LB': InstructionType.I_TYPE,   # Load byte
    'LH': InstructionType.I_TYPE,   # Load halfword
    'LBU': InstructionType.I_TYPE,  # Load byte unsigned
    'LHU': InstructionType.I_TYPE,  # Load halfword unsigned
    
    # Store instructions (S-type)
    'SW': InstructionType.S_TYPE,   # Store word
    'SB': InstructionType.S_TYPE,   # Store byte
    'SH': InstructionType.S_TYPE,   # Store halfword
    
    # Branch instructions (B-type)
    'BEQ': InstructionType.B_TYPE,  # Branch if equal
    'BNE': InstructionType.B_TYPE,  # Branch if not equal
    'BLT': InstructionType.B_TYPE,  # Branch if less than
    'BGE': InstructionType.B_TYPE,  # Branch if greater or equal
    'BLTU': InstructionType.B_TYPE, # Branch if less than unsigned
    'BGEU': InstructionType.B_TYPE, # Branch if greater or equal unsigned
    
    # Jump instructions (J-type)
    'JAL': InstructionType.J_TYPE,  # Jump and link
    'JALR': InstructionType.J_TYPE, # Jump and link register
    
    # Upper immediate (U-type)
    'LUI': InstructionType.U_TYPE,  # Load upper immediate
    'AUIPC': InstructionType.U_TYPE,# Add upper immediate to PC
    
    # CSR instructions (I-type format)
    'CSRRW': InstructionType.I_TYPE,  # CSR read/write
    'CSRRS': InstructionType.I_TYPE,  # CSR read and set bits
    'CSRRC': InstructionType.I_TYPE,  # CSR read and clear bits
    'CSRRWI': InstructionType.I_TYPE, # CSR read/write immediate
    'CSRRSI': InstructionType.I_TYPE, # CSR read and set bits immediate
    'CSRRCI': InstructionType.I_TYPE, # CSR read and clear bits immediate
    
    # System
    'HALT': InstructionType.HALT,
    'MRET': InstructionType.HALT,  # Return from interrupt (like HALT but different semantics)
    'NOP': InstructionType.I_TYPE,  # No operation (implemented as ADDI x0, x0, 0)
}

def parse_register(reg_str):
    """
    Parse a register string to register number
    
    Args:
        reg_str: Register string like 'x5' or '5'
        
    Returns:
        Register number (0-31)
    """
    reg_str = reg_str.strip().lower()
    
    # Handle register names
    if reg_str.startswith('x'):
        reg_str = reg_str[1:]
    
    # Handle aliases
    aliases = {
        'zero': 0,
        'ra': 1,
        'sp': 2,
        'gp': 3,
        'tp': 4,
        'fp': 8,
        's0': 8,
    }
    
    if reg_str in aliases:
        return aliases[reg_str]
    
    try:
        reg_num = int(reg_str)
        if 0 <= reg_num < 32:
            return reg_num
    except ValueError:
        pass
    
    raise ValueError(f"Invalid register: {reg_str}")

def parse_immediate(imm_str):
    """
    Parse an immediate value
    
    Args:
        imm_str: Immediate string (decimal, hex, or binary)
        
    Returns:
        Integer value
    """
    imm_str = imm_str.strip()
    
    # Handle different number formats
    if imm_str.startswith('0x') or imm_str.startswith('0X'):
        return int(imm_str, 16)
    elif imm_str.startswith('0b') or imm_str.startswith('0B'):
        return int(imm_str, 2)
    else:
        return int(imm_str)

def parse_memory_operand(operand):
    """
    Parse memory operand like '100(x5)' or '0(sp)'
    
    Args:
        operand: Memory operand string
        
    Returns:
        Tuple of (offset, base_register)
    """
    operand = operand.strip()
    
    # Find parentheses
    if '(' not in operand or ')' not in operand:
        raise ValueError(f"Invalid memory operand: {operand}")
    
    paren_start = operand.index('(')
    paren_end = operand.index(')')
    
    # Extract offset and register
    offset_str = operand[:paren_start].strip()
    reg_str = operand[paren_start+1:paren_end].strip()
    
    offset = parse_immediate(offset_str) if offset_str else 0
    reg = parse_register(reg_str)
    
    return offset, reg
