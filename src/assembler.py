"""
Assembler module for the RISC VM
Parses assembly source code into instructions
"""

import re
from .instruction import (
    Instruction, InstructionType, INSTRUCTION_SET,
    parse_register, parse_immediate, parse_memory_operand
)

class AssemblerError(Exception):
    """Raised when assembly parsing fails"""
    pass

class Assembler:
    """Assembles text assembly code into executable instructions"""
    
    def __init__(self):
        self.labels = {}  # Map label names to addresses
        self.instructions = []  # List of parsed instructions
        self.data_section = {}  # Data section values
        self.current_address = 0
        
    def assemble(self, source):
        """
        Assemble source code into instructions
        
        Args:
            source: Assembly source code as string
            
        Returns:
            List of Instruction objects
        """
        self.labels = {}
        self.instructions = []
        self.data_section = {}
        self.current_address = 0
        
        # First pass: parse and collect labels
        lines = self._preprocess(source)
        self._first_pass(lines)
        
        # Second pass: resolve labels
        self._second_pass()
        
        return self.instructions
    
    def _preprocess(self, source):
        """
        Preprocess source code: remove comments, clean whitespace
        
        Args:
            source: Raw assembly source
            
        Returns:
            List of cleaned lines
        """
        lines = []
        for line in source.split('\n'):
            # Remove comments (but be careful not to remove comment chars inside character literals)
            # Simple approach: process char literals first, THEN remove comments
            line = self._preprocess_char_literals(line)
            
            # Now remove comments (safe since char literals are already converted to numbers)
            if '#' in line:
                line = line[:line.index('#')]
            if ';' in line:
                line = line[:line.index(';')]
            
            # Clean whitespace
            line = line.strip()
            
            # Skip empty lines
            if line:
                lines.append(line)
        
        return lines
    
    def _preprocess_char_literals(self, line):
        """
        Convert character literals ('A', '\n', etc.) to their ASCII values
        
        Args:
            line: Assembly line that may contain character literals
            
        Returns:
            Line with character literals replaced by numeric values
        """
        def replace_char(match):
            """Replace a single character literal match"""
            char_content = match.group(1)
            
            # Handle escape sequences
            if len(char_content) == 2 and char_content[0] == '\\':
                escape_map = {
                    'n': 10,   # newline
                    't': 9,    # tab
                    'r': 13,   # carriage return
                    '0': 0,    # null
                    "'": 39,   # single quote
                    '\\': 92   # backslash
                }
                escape_char = char_content[1]
                if escape_char in escape_map:
                    return str(escape_map[escape_char])
                else:
                    raise AssemblerError(f"Unknown escape sequence: '\\{escape_char}'")
            
            # Handle single character
            elif len(char_content) == 1:
                return str(ord(char_content))
            
            # Handle empty or multi-character (error)
            elif len(char_content) == 0:
                raise AssemblerError("Empty character literal ''")
            else:
                raise AssemblerError(f"Multi-character literal not supported: '{char_content}'")
        
        # First check for invalid character literals (empty or multi-char) and raise errors
        # Check for empty character literal '' (but not '\'' which is escaped quote)
        # Look for '' that's not preceded by backslash
        if re.search(r"(?<!\\)''", line):
            raise AssemblerError("Empty character literal ''")
        
        # Check for multi-character literals (simple heuristic: more than 2 chars between quotes)
        # This catches 'AB', 'ABC', etc. but allows '\n' (2 chars for escape)
        multi_char_pattern = r"'[^']{3,}'"
        if re.search(multi_char_pattern, line):
            match = re.search(multi_char_pattern, line)
            raise AssemblerError(f"Multi-character literal not supported: {match.group(0)}")
        
        # Also catch cases like 'AB' (2 non-escape chars)
        two_char_pattern = r"'[^'\\]{2}'"
        if re.search(two_char_pattern, line):
            match = re.search(two_char_pattern, line)
            raise AssemblerError(f"Multi-character literal not supported: {match.group(0)}")
        
        # Now match and replace valid single-quoted character literals: 'X' or '\n'
        # Pattern: ' followed by (single non-quote/backslash char OR backslash+char) followed by '
        pattern = r"'([^'\\]|\\.)'"
        
        try:
            return re.sub(pattern, replace_char, line)
        except AssemblerError:
            # Re-raise assembler errors as-is
            raise
        except Exception as e:
            raise AssemblerError(f"Error processing character literal: {str(e)}")
    
    def _first_pass(self, lines):
        """
        First pass: parse instructions and collect labels
        
        Args:
            lines: List of preprocessed source lines
        """
        current_section = '.text'
        
        for line_num, line in enumerate(lines, start=1):
            try:
                # Check for section directives
                if line.startswith('.'):
                    if line == '.text':
                        current_section = '.text'
                        self.current_address = 0x00000  # Text starts at 0
                    elif line == '.data':
                        current_section = '.data'
                        self.current_address = 0x10000  # Data starts at 64KB
                    continue
                
                # Check for label
                if ':' in line:
                    label_name, _, rest = line.partition(':')
                    label_name = label_name.strip()
                    self.labels[label_name] = self.current_address
                    line = rest.strip()
                    
                    if not line:
                        continue
                
                # Parse instruction
                if current_section == '.text':
                    instruction = self._parse_instruction(line)
                    self.instructions.append(instruction)
                    self.current_address += 4  # Each instruction is 4 bytes
                elif current_section == '.data':
                    self._parse_data_directive(line)
                
            except Exception as e:
                raise AssemblerError(f"Error on line {line_num}: {line}\n{str(e)}")
    
    def _second_pass(self):
        """Second pass: resolve label references to addresses"""
        for instruction in self.instructions:
            if instruction.label:
                if instruction.label not in self.labels:
                    raise AssemblerError(f"Undefined label: {instruction.label}")
                
                target_addr = self.labels[instruction.label]
                
                # Calculate relative offset for branches
                if instruction.type == InstructionType.B_TYPE:
                    # Branch offset is relative to current instruction
                    current_addr = self.instructions.index(instruction) * 4
                    instruction.imm = target_addr - current_addr
                elif instruction.type == InstructionType.J_TYPE:
                    # Jump offset is also relative
                    current_addr = self.instructions.index(instruction) * 4
                    instruction.imm = target_addr - current_addr
                elif instruction.type == InstructionType.I_TYPE:
                    # For I-type, use absolute address as immediate
                    instruction.imm = target_addr
    
    def _parse_instruction(self, line):
        """
        Parse a single instruction line
        
        Args:
            line: Instruction line (without label)
            
        Returns:
            Instruction object
        """
        # Split into parts
        parts = re.split(r'[,\s]+', line)
        opcode = parts[0].upper()
        
        if opcode not in INSTRUCTION_SET:
            raise AssemblerError(f"Unknown instruction: {opcode}")
        
        inst_type = INSTRUCTION_SET[opcode]
        
        # Parse based on instruction type
        if inst_type == InstructionType.HALT:
            return Instruction(opcode, inst_type)
        
        elif inst_type == InstructionType.R_TYPE:
            # Format: ADD x1, x2, x3
            if len(parts) < 4:
                raise AssemblerError(f"R-type instruction requires 3 operands: {line}")
            rd = parse_register(parts[1])
            rs1 = parse_register(parts[2])
            rs2 = parse_register(parts[3])
            return Instruction(opcode, inst_type, rd=rd, rs1=rs1, rs2=rs2)
        
        elif inst_type == InstructionType.I_TYPE:
            if opcode in ['LW', 'LB', 'LH', 'LBU', 'LHU']:
                # Format: LW x1, 100(x2)
                if len(parts) < 3:
                    raise AssemblerError(f"Load instruction requires 2 operands: {line}")
                rd = parse_register(parts[1])
                
                # Reconstruct the memory operand (might have been split by comma)
                mem_operand = ''.join(parts[2:])
                offset, rs1 = parse_memory_operand(mem_operand)
                return Instruction(opcode, inst_type, rd=rd, rs1=rs1, imm=offset)
            elif opcode == 'NOP':
                # NOP is encoded as ADDI x0, x0, 0
                return Instruction('ADDI', inst_type, rd=0, rs1=0, imm=0)
            elif opcode in ['CSRRW', 'CSRRS', 'CSRRC']:
                # Format: CSRRW x1, 0x300, x2 (rd, csr, rs1)
                if len(parts) < 4:
                    raise AssemblerError(f"CSR instruction requires 3 operands: {line}")
                rd = parse_register(parts[1])
                csr = parse_immediate(parts[2])  # CSR address (e.g., 0x300)
                rs1 = parse_register(parts[3])
                return Instruction(opcode, inst_type, rd=rd, rs1=rs1, imm=csr)
            elif opcode in ['CSRRWI', 'CSRRSI', 'CSRRCI']:
                # Format: CSRRWI x1, 0x300, 5 (rd, csr, uimm)
                if len(parts) < 4:
                    raise AssemblerError(f"CSR immediate instruction requires 3 operands: {line}")
                rd = parse_register(parts[1])
                csr = parse_immediate(parts[2])  # CSR address
                uimm = parse_immediate(parts[3])  # 5-bit unsigned immediate
                # Store uimm in rs1 field for CSR immediate instructions
                return Instruction(opcode, inst_type, rd=rd, rs1=uimm, imm=csr)
            else:
                # Format: ADDI x1, x2, 100 or ADDI x1, x2, label
                if len(parts) < 4:
                    raise AssemblerError(f"I-type instruction requires 3 operands: {line}")
                rd = parse_register(parts[1])
                rs1 = parse_register(parts[2])
                
                # Check if it's a label or immediate
                target = parts[3]
                try:
                    imm = parse_immediate(target)
                    return Instruction(opcode, inst_type, rd=rd, rs1=rs1, imm=imm)
                except ValueError:
                    # It's a label
                    return Instruction(opcode, inst_type, rd=rd, rs1=rs1, label=target)
        
        elif inst_type == InstructionType.S_TYPE:
            # Format: SW x1, 100(x2)
            if len(parts) < 3:
                raise AssemblerError(f"Store instruction requires 2 operands: {line}")
            rs2 = parse_register(parts[1])
            
            # Reconstruct the memory operand
            mem_operand = ''.join(parts[2:])
            offset, rs1 = parse_memory_operand(mem_operand)
            return Instruction(opcode, inst_type, rs1=rs1, rs2=rs2, imm=offset)
        
        elif inst_type == InstructionType.B_TYPE:
            # Format: BEQ x1, x2, label or BEQ x1, x2, 100
            if len(parts) < 4:
                raise AssemblerError(f"Branch instruction requires 3 operands: {line}")
            rs1 = parse_register(parts[1])
            rs2 = parse_register(parts[2])
            
            # Check if it's a label or immediate
            target = parts[3]
            try:
                imm = parse_immediate(target)
                return Instruction(opcode, inst_type, rs1=rs1, rs2=rs2, imm=imm)
            except ValueError:
                # It's a label
                return Instruction(opcode, inst_type, rs1=rs1, rs2=rs2, label=target)
        
        elif inst_type == InstructionType.J_TYPE:
            if opcode == 'JAL':
                # Format: JAL x1, label or JAL x1, 100
                if len(parts) < 3:
                    raise AssemblerError(f"JAL requires 2 operands: {line}")
                rd = parse_register(parts[1])
                target = parts[2]
                
                try:
                    imm = parse_immediate(target)
                    return Instruction(opcode, inst_type, rd=rd, imm=imm)
                except ValueError:
                    return Instruction(opcode, inst_type, rd=rd, label=target)
            
            elif opcode == 'JALR':
                # Format: JALR x1, x2, 100
                if len(parts) < 4:
                    raise AssemblerError(f"JALR requires 3 operands: {line}")
                rd = parse_register(parts[1])
                rs1 = parse_register(parts[2])
                imm = parse_immediate(parts[3])
                return Instruction(opcode, inst_type, rd=rd, rs1=rs1, imm=imm)
        
        elif inst_type == InstructionType.U_TYPE:
            # Format: LUI x1, 0x12345
            if len(parts) < 3:
                raise AssemblerError(f"U-type instruction requires 2 operands: {line}")
            rd = parse_register(parts[1])
            imm = parse_immediate(parts[2])
            return Instruction(opcode, inst_type, rd=rd, imm=imm)
        
        elif inst_type == InstructionType.HALT:
            # HALT, MRET, and WFI take no operands
            if opcode in ['HALT', 'MRET', 'WFI']:
                return Instruction(opcode, inst_type)
        
        raise AssemblerError(f"Could not parse instruction: {line}")
    
    def _parse_data_directive(self, line):
        """Parse data section directive (.word, .string, etc.)"""
        # TODO: Implement data section support
        pass
    
    def get_labels(self):
        """Get dictionary of labels and their addresses"""
        return self.labels.copy()
