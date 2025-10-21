"""
Virtual Machine for RISC Assembly
Main execution engine that ties together CPU, Memory, Display, and Assembler
"""

import logging

from .cpu import CPU
from .memory import Memory, MemoryAccessError, MemoryProtectionError
from .display import Display
from .timer import Timer
from .realtime_timer import RealTimeTimer
from .assembler import Assembler, AssemblerError
from .instruction import InstructionType

logger = logging.getLogger(__name__)

class VMError(Exception):
    """Base exception for VM errors"""
    pass

class VirtualMachine:
    """
    RISC Virtual Machine
    Executes RISC assembly programs with memory-mapped display
    """
    
    def __init__(self, debug=False, protect_text=False):
        """
        Initialize the virtual machine
        
        Args:
            debug: Enable debug output
            protect_text: Protect text segment from writes
        """
        self.display = Display()
        self.timer = Timer()
        self.rt_timer = RealTimeTimer()
        self.memory = Memory(display=self.display, timer=self.timer, rt_timer=self.rt_timer, protect_text=protect_text)
        self.cpu = CPU()
        self.assembler = Assembler()
        self.debug = debug
        self.breakpoints = set()
        self.instructions = []
        
    def load_program(self, source):
        """
        Load and assemble a program
        
        Args:
            source: Assembly source code as string
        """
        try:
            # Assemble the program
            self.instructions = self.assembler.assemble(source)
            
            if self.debug:
                print(f"Assembled {len(self.instructions)} instructions")
                print(f"Labels: {self.assembler.get_labels()}")
            
            # Reset CPU and timers
            self.cpu.reset()
            self.cpu.pc = 0
            self.timer.reset()
            self.rt_timer.reset()
            
            # Initialize stack pointer to top of stack (must be 4-byte aligned)
            self.cpu.write_register(2, 0xBFFFC)  # x2 (sp)
            
        except AssemblerError as e:
            raise VMError(f"Assembly error: {e}")
    
    def step(self):
        """
        Execute a single instruction
        
        Returns:
            True if execution should continue, False if halted
        """
        if self.cpu.halted:
            return False
        
        # Tick the cycle-based timer
        tick_result = self.timer.tick()
        if self.debug and (self.cpu.waiting_for_interrupt or self.cpu.pc >= 0x30):
            if self.timer.counter % 5 == 0 or self.cpu.pc >= 0x30:
                logger.debug(f"  Timer state: counter={self.timer.counter}, compare={self.timer.compare}, control=0x{self.timer.control:02X}, enabled={bool(self.timer.control & 0x01)}, tick={tick_result}")
        if tick_result:
            # Cycle-based timer interrupt occurred
            if self.debug:
                logger.debug(f"  TIMER FIRED! Setting interrupt pending")
            self.cpu.set_interrupt_pending(self.cpu.MIE_MTIE)
        
        # Check real-time timer
        if self.rt_timer.check():
            # Real-time timer interrupt occurred
            self.cpu.set_interrupt_pending(self.cpu.MIE_RTIE)
        
        # Check for pending interrupts before fetching instruction
        if self.cpu.has_pending_interrupts():
            interrupt_code = self.cpu.get_highest_priority_interrupt()
            if interrupt_code is not None:
                # Wake from WFI if waiting
                if self.cpu.waiting_for_interrupt:
                    self.cpu.wake_from_wait()
                    if self.debug:
                        logger.debug(f"CPU woken from wait by interrupt 0x{interrupt_code:08X}")
                
                if self.debug:
                    logger.debug(f"\n*** Interrupt 0x{interrupt_code:08X} at PC=0x{self.cpu.pc:08X} ***")
                self.cpu.enter_interrupt(interrupt_code)
                # Clear appropriate interrupt pending bit
                if interrupt_code == self.cpu.INT_TIMER:
                    self.cpu.clear_interrupt_pending(self.cpu.MIE_MTIE)
                elif interrupt_code == self.cpu.INT_TIMER_REALTIME:
                    self.cpu.clear_interrupt_pending(self.cpu.MIE_RTIE)
        
        # If CPU is waiting for interrupt, don't execute instructions
        if self.cpu.waiting_for_interrupt:
            # Still count as a cycle (timers are ticking)
            self.cpu.instruction_count += 1
            if self.debug:
                logger.debug(f"[0x{self.cpu.pc:08X}] (waiting for interrupt)")
            
            # Add small sleep to allow real-time to pass for RT timer
            # This prevents burning through instruction limit while waiting
            import time
            time.sleep(0.00001)  # 10 microseconds - allows RT timer to fire
            
            return True
        
        # Check if PC is valid
        instruction_index = self.cpu.pc // 4
        if instruction_index < 0 or instruction_index >= len(self.instructions):
            raise VMError(f"PC out of bounds: 0x{self.cpu.pc:08X}")
        
        # Fetch instruction
        instruction = self.instructions[instruction_index]
        
        if self.debug:
            logger.debug(f"\n[0x{self.cpu.pc:08X}] {instruction}")
        
        # Check breakpoint
        if self.cpu.pc in self.breakpoints:
            logger.info(f"Breakpoint hit at 0x{self.cpu.pc:08X}")
            return False
        
        # Execute instruction
        try:
            self._execute(instruction)
            self.cpu.instruction_count += 1
        except Exception as e:
            raise VMError(f"Execution error at PC=0x{self.cpu.pc:08X}: {e}")
        
        return not self.cpu.halted
    
    def run(self, max_instructions=1000000, live_display=False, update_interval=10000):
        """
        Run the program until halt or max instructions
        
        Args:
            max_instructions: Maximum number of instructions to execute
            live_display: If True, update display during execution
            update_interval: Number of instructions between display updates
            
        Returns:
            Number of instructions executed
        """
        import sys
        count = 0
        
        if live_display:
            # Clear screen and hide cursor
            print("\033[2J\033[?25l", end='', flush=True)
        
        try:
            while count < max_instructions and self.step():
                count += 1
                
                # Update display periodically if live display is enabled
                if live_display and count % update_interval == 0:
                    # Move cursor to home position and render
                    print("\033[H", end='', flush=True)
                    self.display.render()
                    print(f"\nInstructions: {count:,}", flush=True)
            
            if count >= max_instructions:
                if not live_display:
                    logger.warning(f"Execution stopped after {max_instructions} instructions")
        finally:
            if live_display:
                # Show cursor again
                print("\033[?25h", end='', flush=True)
        
        return count
    
    def _execute(self, instruction):
        """Execute a single instruction"""
        opcode = instruction.opcode
        
        # R-type instructions
        if instruction.type == InstructionType.R_TYPE:
            self._execute_r_type(instruction)
        
        # I-type instructions
        elif instruction.type == InstructionType.I_TYPE:
            self._execute_i_type(instruction)
        
        # S-type instructions (stores)
        elif instruction.type == InstructionType.S_TYPE:
            self._execute_s_type(instruction)
        
        # B-type instructions (branches)
        elif instruction.type == InstructionType.B_TYPE:
            self._execute_b_type(instruction)
        
        # J-type instructions (jumps)
        elif instruction.type == InstructionType.J_TYPE:
            self._execute_j_type(instruction)
        
        # U-type instructions
        elif instruction.type == InstructionType.U_TYPE:
            self._execute_u_type(instruction)
        
        # System instructions
        elif instruction.type == InstructionType.HALT:
            if opcode == 'HALT':
                self.cpu.halt()
                if self.debug:
                    print("CPU halted")
            elif opcode == 'MRET':
                # Return from interrupt
                self.cpu.return_from_interrupt()
                if self.debug:
                    logger.debug(f"Return from interrupt to PC=0x{self.cpu.pc:08X}")
                return  # Don't increment PC, MRET sets it
            elif opcode == 'WFI':
                # Wait for interrupt
                # Warning if interrupts are disabled (potential deadlock)
                if not self.cpu.interrupt_enabled:
                    logger.warning(f"WFI at PC=0x{self.cpu.pc:08X} with interrupts disabled - potential deadlock!")
                self.cpu.wait_for_interrupt()
                if self.debug:
                    logger.debug(f"CPU entering wait-for-interrupt state at PC=0x{self.cpu.pc:08X}")
                self.cpu.increment_pc()  # Advance PC so we resume after WFI
                return  # Don't increment PC again
        
        else:
            raise VMError(f"Unknown instruction type: {instruction.type}")
    
    def _execute_r_type(self, inst):
        """Execute R-type instruction"""
        rs1_val = self.cpu.read_register(inst.rs1)
        rs2_val = self.cpu.read_register(inst.rs2)
        
        if inst.opcode == 'ADD':
            result = (rs1_val + rs2_val) & 0xFFFFFFFF
        elif inst.opcode == 'SUB':
            result = (rs1_val - rs2_val) & 0xFFFFFFFF
        elif inst.opcode == 'AND':
            result = rs1_val & rs2_val
        elif inst.opcode == 'OR':
            result = rs1_val | rs2_val
        elif inst.opcode == 'XOR':
            result = rs1_val ^ rs2_val
        elif inst.opcode == 'SLL':
            result = (rs1_val << (rs2_val & 0x1F)) & 0xFFFFFFFF
        elif inst.opcode == 'SRL':
            result = rs1_val >> (rs2_val & 0x1F)
        elif inst.opcode == 'SRA':
            # Arithmetic shift (sign-extend)
            shift = rs2_val & 0x1F
            result = self.cpu.to_unsigned(self.cpu.to_signed(rs1_val) >> shift)
        elif inst.opcode == 'SLT':
            result = 1 if self.cpu.to_signed(rs1_val) < self.cpu.to_signed(rs2_val) else 0
        elif inst.opcode == 'SLTU':
            result = 1 if rs1_val < rs2_val else 0
        else:
            raise VMError(f"Unknown R-type instruction: {inst.opcode}")
        
        self.cpu.write_register(inst.rd, result)
        self.cpu.increment_pc()
    
    def _execute_i_type(self, inst):
        """Execute I-type instruction"""
        rs1_val = self.cpu.read_register(inst.rs1)
        imm = self.cpu.sign_extend(inst.imm & 0xFFF, 12)  # 12-bit immediate
        
        if inst.opcode == 'ADDI':
            result = (rs1_val + imm) & 0xFFFFFFFF
            self.cpu.write_register(inst.rd, result)
        elif inst.opcode == 'ANDI':
            result = rs1_val & imm
            self.cpu.write_register(inst.rd, result)
        elif inst.opcode == 'ORI':
            result = rs1_val | imm
            self.cpu.write_register(inst.rd, result)
        elif inst.opcode == 'XORI':
            result = rs1_val ^ imm
            self.cpu.write_register(inst.rd, result)
        elif inst.opcode == 'SLLI':
            shamt = inst.imm & 0x1F
            result = (rs1_val << shamt) & 0xFFFFFFFF
            self.cpu.write_register(inst.rd, result)
        elif inst.opcode == 'SRLI':
            shamt = inst.imm & 0x1F
            result = rs1_val >> shamt
            self.cpu.write_register(inst.rd, result)
        elif inst.opcode == 'SRAI':
            shamt = inst.imm & 0x1F
            result = self.cpu.to_unsigned(self.cpu.to_signed(rs1_val) >> shamt)
            self.cpu.write_register(inst.rd, result)
        elif inst.opcode == 'SLTI':
            result = 1 if self.cpu.to_signed(rs1_val) < self.cpu.to_signed(imm) else 0
            self.cpu.write_register(inst.rd, result)
        elif inst.opcode == 'SLTIU':
            result = 1 if rs1_val < (imm & 0xFFFFFFFF) else 0
            self.cpu.write_register(inst.rd, result)
        
        # Load instructions
        elif inst.opcode == 'LW':
            addr = (rs1_val + imm) & 0xFFFFFFFF
            value = self.memory.read_word(addr)
            self.cpu.write_register(inst.rd, value)
        elif inst.opcode == 'LB':
            addr = (rs1_val + imm) & 0xFFFFFFFF
            value = self.memory.read_byte(addr)
            value = self.cpu.sign_extend(value, 8)
            self.cpu.write_register(inst.rd, value)
        elif inst.opcode == 'LBU':
            addr = (rs1_val + imm) & 0xFFFFFFFF
            value = self.memory.read_byte(addr)
            self.cpu.write_register(inst.rd, value)
        elif inst.opcode == 'LH':
            addr = (rs1_val + imm) & 0xFFFFFFFF
            b0 = self.memory.read_byte(addr)
            b1 = self.memory.read_byte(addr + 1)
            value = b0 | (b1 << 8)
            value = self.cpu.sign_extend(value, 16)
            self.cpu.write_register(inst.rd, value)
        elif inst.opcode == 'LHU':
            addr = (rs1_val + imm) & 0xFFFFFFFF
            b0 = self.memory.read_byte(addr)
            b1 = self.memory.read_byte(addr + 1)
            value = b0 | (b1 << 8)
            self.cpu.write_register(inst.rd, value)
        
        # CSR instructions (imm field contains CSR address)
        elif inst.opcode == 'CSRRW':
            # Read CSR, write rs1 to CSR, return old value
            csr_addr = inst.imm & 0xFFF
            old_value = self.cpu.read_csr(csr_addr)
            self.cpu.write_csr(csr_addr, rs1_val)
            self.cpu.write_register(inst.rd, old_value)
        elif inst.opcode == 'CSRRS':
            # Read CSR, set bits from rs1, return old value
            csr_addr = inst.imm & 0xFFF
            old_value = self.cpu.set_csr_bits(csr_addr, rs1_val)
            self.cpu.write_register(inst.rd, old_value)
        elif inst.opcode == 'CSRRC':
            # Read CSR, clear bits from rs1, return old value
            csr_addr = inst.imm & 0xFFF
            old_value = self.cpu.clear_csr_bits(csr_addr, rs1_val)
            self.cpu.write_register(inst.rd, old_value)
        elif inst.opcode == 'CSRRWI':
            # Read CSR, write immediate (rs1 field) to CSR, return old value
            csr_addr = inst.imm & 0xFFF
            uimm = inst.rs1 & 0x1F  # rs1 field contains 5-bit immediate
            old_value = self.cpu.read_csr(csr_addr)
            self.cpu.write_csr(csr_addr, uimm)
            self.cpu.write_register(inst.rd, old_value)
        elif inst.opcode == 'CSRRSI':
            # Read CSR, set bits from immediate, return old value
            csr_addr = inst.imm & 0xFFF
            uimm = inst.rs1 & 0x1F
            old_value = self.cpu.set_csr_bits(csr_addr, uimm)
            self.cpu.write_register(inst.rd, old_value)
        elif inst.opcode == 'CSRRCI':
            # Read CSR, clear bits from immediate, return old value
            csr_addr = inst.imm & 0xFFF
            uimm = inst.rs1 & 0x1F
            old_value = self.cpu.clear_csr_bits(csr_addr, uimm)
            self.cpu.write_register(inst.rd, old_value)
        else:
            raise VMError(f"Unknown I-type instruction: {inst.opcode}")
        
        self.cpu.increment_pc()
    
    def _execute_s_type(self, inst):
        """Execute S-type instruction (stores)"""
        rs1_val = self.cpu.read_register(inst.rs1)
        rs2_val = self.cpu.read_register(inst.rs2)
        imm = self.cpu.sign_extend(inst.imm & 0xFFF, 12)
        addr = (rs1_val + imm) & 0xFFFFFFFF
        
        if self.debug:
            logger.debug(f"SW: rs1=x{inst.rs1}=0x{rs1_val:08X} + imm={imm} = addr=0x{addr:08X}, value=0x{rs2_val:08X}")
        
        if inst.opcode == 'SW':
            self.memory.write_word(addr, rs2_val)
        elif inst.opcode == 'SB':
            self.memory.write_byte(addr, rs2_val & 0xFF)
        elif inst.opcode == 'SH':
            self.memory.write_byte(addr, rs2_val & 0xFF)
            self.memory.write_byte(addr + 1, (rs2_val >> 8) & 0xFF)
        else:
            raise VMError(f"Unknown S-type instruction: {inst.opcode}")
        
        self.cpu.increment_pc()
    
    def _execute_b_type(self, inst):
        """Execute B-type instruction (branches)"""
        rs1_val = self.cpu.read_register(inst.rs1)
        rs2_val = self.cpu.read_register(inst.rs2)
        
        branch_taken = False
        
        if inst.opcode == 'BEQ':
            branch_taken = (rs1_val == rs2_val)
        elif inst.opcode == 'BNE':
            branch_taken = (rs1_val != rs2_val)
        elif inst.opcode == 'BLT':
            branch_taken = (self.cpu.to_signed(rs1_val) < self.cpu.to_signed(rs2_val))
        elif inst.opcode == 'BGE':
            branch_taken = (self.cpu.to_signed(rs1_val) >= self.cpu.to_signed(rs2_val))
        elif inst.opcode == 'BLTU':
            branch_taken = (rs1_val < rs2_val)
        elif inst.opcode == 'BGEU':
            branch_taken = (rs1_val >= rs2_val)
        else:
            raise VMError(f"Unknown B-type instruction: {inst.opcode}")
        
        if branch_taken:
            offset = self.cpu.sign_extend(inst.imm & 0x1FFF, 13)
            new_pc = (self.cpu.pc + offset) & 0xFFFFFFFF
            self.cpu.set_pc(new_pc)
        else:
            self.cpu.increment_pc()
    
    def _execute_j_type(self, inst):
        """Execute J-type instruction (jumps)"""
        if inst.opcode == 'JAL':
            # Save return address (PC + 4)
            self.cpu.write_register(inst.rd, self.cpu.pc + 4)
            
            # Jump to target
            offset = self.cpu.sign_extend(inst.imm & 0xFFFFF, 20)
            new_pc = (self.cpu.pc + offset) & 0xFFFFFFFF
            self.cpu.set_pc(new_pc)
        
        elif inst.opcode == 'JALR':
            # Save return address
            return_addr = self.cpu.pc + 4
            
            # Jump to rs1 + offset
            rs1_val = self.cpu.read_register(inst.rs1)
            offset = self.cpu.sign_extend(inst.imm & 0xFFF, 12)
            new_pc = (rs1_val + offset) & 0xFFFFFFFE  # Clear LSB
            
            self.cpu.write_register(inst.rd, return_addr)
            self.cpu.set_pc(new_pc)
        else:
            raise VMError(f"Unknown J-type instruction: {inst.opcode}")
    
    def _execute_u_type(self, inst):
        """Execute U-type instruction"""
        if inst.opcode == 'LUI':
            # Load upper 20 bits, lower 12 bits are 0
            value = (inst.imm & 0xFFFFF) << 12
            self.cpu.write_register(inst.rd, value)
        elif inst.opcode == 'AUIPC':
            # Add upper immediate to PC
            value = ((inst.imm & 0xFFFFF) << 12) + self.cpu.pc
            self.cpu.write_register(inst.rd, value & 0xFFFFFFFF)
        else:
            raise VMError(f"Unknown U-type instruction: {inst.opcode}")
        
        self.cpu.increment_pc()
    
    def add_breakpoint(self, address):
        """Add a breakpoint at the given address"""
        self.breakpoints.add(address)
    
    def remove_breakpoint(self, address):
        """Remove a breakpoint"""
        self.breakpoints.discard(address)
    
    def get_state(self):
        """Get current VM state for debugging"""
        return {
            'pc': self.cpu.pc,
            'registers': self.cpu.registers.copy(),
            'instruction_count': self.cpu.instruction_count,
            'halted': self.cpu.halted
        }
    
    def dump_state(self):
        """Print current VM state"""
        print("\n" + "="*70)
        print(self.cpu.dump_registers())
        print("="*70)
