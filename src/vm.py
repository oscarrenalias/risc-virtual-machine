"""
Virtual Machine for RISC Assembly
Main execution engine that ties together CPU, Memory, Display, and Assembler
"""

import logging
from typing import Optional

from .cpu import CPU
from .cpu_clock import CPUClock
from .memory import Memory, MemoryAccessError, MemoryProtectionError
from .display import Display
from .timer import Timer
from .realtime_timer import RealTimeTimer
from .assembler import Assembler, AssemblerError
from .instruction import InstructionType
from .debugger import format_exception_report

logger = logging.getLogger(__name__)

class VMError(Exception):
    """
    Enhanced VM exception with detailed debugging information
    
    This exception captures the full state of the VM at the time of the error,
    including CPU registers, stack, instruction context, and more.
    """
    
    def __init__(self, message: str, cpu=None, memory=None, instructions=None, 
                 fault_address: Optional[int] = None, original_exception: Optional[Exception] = None):
        """
        Initialize VMError with debugging context
        
        Args:
            message: Error message
            cpu: CPU instance at time of error
            memory: Memory instance at time of error
            instructions: List of instructions
            fault_address: Memory address that caused the fault (if applicable)
            original_exception: The original exception that was caught
        """
        super().__init__(message)
        self.cpu = cpu
        self.memory = memory
        self.instructions = instructions
        self.fault_address = fault_address
        self.original_exception = original_exception
        self.detailed_report = None
        
        # Generate detailed report if we have the necessary context
        # Only generate if we're not already a VMError being re-raised
        if cpu and memory and not isinstance(original_exception, VMError):
            try:
                self.detailed_report = format_exception_report(
                    cpu, memory, instructions or [], 
                    original_exception or self,
                    fault_address
                )
            except Exception as e:
                # If report generation fails, at least preserve the basic error
                logger.error(f"Failed to generate exception report: {e}")
                self.detailed_report = None
    
    def __str__(self):
        """Return detailed error report if available, otherwise basic message"""
        if self.detailed_report:
            return self.detailed_report
        return super().__str__()

class VirtualMachine:
    """
    RISC Virtual Machine
    Executes RISC assembly programs with memory-mapped display
    """
    
    def __init__(self, debug=False, protect_text=False, cpu_clock_hz=1000, enable_clock=True):
        """
        Initialize the virtual machine
        
        Args:
            debug: Enable debug output
            protect_text: Protect text segment from writes
            cpu_clock_hz: CPU clock frequency in Hz (1-10000). Default: 1000 Hz (1 kHz)
            enable_clock: If False, run at maximum speed (no clock delays). Default: True
        """
        self.display = Display()
        self.timer = Timer()
        self.rt_timer = RealTimeTimer()
        self.memory = Memory(display=self.display, timer=self.timer, rt_timer=self.rt_timer, protect_text=protect_text)
        self.cpu = CPU()
        self.cpu_clock = CPUClock(frequency_hz=cpu_clock_hz, enabled=enable_clock)
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
            
            # Load data section into memory
            data_section = self.assembler.get_data_section()
            for address, byte_value in data_section.items():
                self.memory.write_byte(address, byte_value)
            
            if self.debug:
                print(f"Assembled {len(self.instructions)} instructions")
                print(f"Labels: {self.assembler.get_labels()}")
                if data_section:
                    print(f"Data section: {len(data_section)} bytes loaded")
            
            # Reset CPU and timers
            self.cpu.reset()
            self.cpu.pc = 0
            self.timer.reset()
            self.rt_timer.reset()
            self.cpu_clock.reset()
            
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
            
            # Tick CPU clock to maintain timing even during WFI
            # This allows real-time timer to work correctly
            self.cpu_clock.tick()
            
            return True
        
        # Check if PC is valid
        instruction_index = self.cpu.pc // 4
        if instruction_index < 0 or instruction_index >= len(self.instructions):
            raise VMError(
                f"PC out of bounds: 0x{self.cpu.pc:08X}",
                cpu=self.cpu,
                memory=self.memory,
                instructions=self.instructions
            )
        
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
        except (MemoryAccessError, MemoryProtectionError) as e:
            # Extract fault address from memory errors if possible
            fault_addr = None
            error_msg = str(e)
            # Try to parse address from error message (e.g., "Memory access out of bounds: 0x12345678")
            import re
            addr_match = re.search(r'0x([0-9A-Fa-f]+)', error_msg)
            if addr_match:
                try:
                    fault_addr = int(addr_match.group(1), 16)
                except ValueError:
                    pass
            
            raise VMError(
                f"Execution error at PC=0x{self.cpu.pc:08X}: {e}",
                cpu=self.cpu,
                memory=self.memory,
                instructions=self.instructions,
                fault_address=fault_addr,
                original_exception=e
            )
        except Exception as e:
            raise VMError(
                f"Execution error at PC=0x{self.cpu.pc:08X}: {e}",
                cpu=self.cpu,
                memory=self.memory,
                instructions=self.instructions,
                original_exception=e
            )
        
        # Tick the CPU clock to enforce timing
        self.cpu_clock.tick()
        
        return not self.cpu.halted
    
    def run(self, max_instructions=1000000, visualizer=None):
        """
        Run the program until halt or max instructions
        
        Args:
            max_instructions: Maximum number of instructions to execute
            visualizer: Optional VMVisualizer instance for live visualization with display + CPU state
            
        Returns:
            Number of instructions executed
        """
        import sys
        count = 0
        
        # Determine if we're using visualization
        use_visualizer = visualizer is not None and visualizer.can_show_split
        
        # Calculate update interval based on clock speed for better responsiveness
        # At low clock speeds, update more frequently so user sees progress
        update_interval = 10000  # Default for fast execution
        if self.cpu_clock.enabled and use_visualizer:
            if self.cpu_clock.frequency <= 10:
                # Very slow: update every instruction
                update_interval = 1
            elif self.cpu_clock.frequency <= 100:
                # Slow: update every 10 instructions
                update_interval = 10
            elif self.cpu_clock.frequency <= 1000:
                # Medium: update every 100 instructions
                update_interval = 100
            # else: use default update_interval (for fast clocks or no clock)
        
        try:
            while count < max_instructions and self.step():
                count += 1
                
                # Update visualization periodically if visualizer is enabled
                if use_visualizer and count % update_interval == 0:
                    # Use visualizer with CPU panel and display
                    visualizer.render_live_mode_update(count)
            
            if count >= max_instructions:
                if not use_visualizer:
                    logger.warning(f"Execution stopped after {max_instructions} instructions")
        finally:
            pass
        
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
            raise VMError(
                f"Unknown instruction type: {instruction.type}",
                cpu=self.cpu,
                memory=self.memory,
                instructions=self.instructions
            )
    
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
        # M-extension: Multiply/Divide
        elif inst.opcode == 'MUL':
            # Multiply - return lower 32 bits
            signed_rs1 = self.cpu.to_signed(rs1_val)
            signed_rs2 = self.cpu.to_signed(rs2_val)
            product = signed_rs1 * signed_rs2
            result = product & 0xFFFFFFFF
        elif inst.opcode == 'DIV':
            # Signed division
            signed_rs1 = self.cpu.to_signed(rs1_val)
            signed_rs2 = self.cpu.to_signed(rs2_val)
            if signed_rs2 == 0:
                # Division by zero: return -1
                result = 0xFFFFFFFF
            elif signed_rs1 == -2147483648 and signed_rs2 == -1:
                # Overflow case: -2^31 / -1 would be 2^31 (overflow)
                result = 0x80000000
            else:
                # Python's // rounds toward negative infinity, but RISC-V rounds toward zero
                quotient = int(signed_rs1 / signed_rs2)
                result = self.cpu.to_unsigned(quotient)
        elif inst.opcode == 'DIVU':
            # Unsigned division
            if rs2_val == 0:
                # Division by zero: return 2^32-1
                result = 0xFFFFFFFF
            else:
                result = rs1_val // rs2_val
        elif inst.opcode == 'REM':
            # Signed remainder
            signed_rs1 = self.cpu.to_signed(rs1_val)
            signed_rs2 = self.cpu.to_signed(rs2_val)
            if signed_rs2 == 0:
                # Division by zero: return dividend
                result = rs1_val
            elif signed_rs1 == -2147483648 and signed_rs2 == -1:
                # Overflow case: remainder is 0
                result = 0
            else:
                # Python's % has different semantics, use actual formula
                quotient = int(signed_rs1 / signed_rs2)
                remainder = signed_rs1 - (quotient * signed_rs2)
                result = self.cpu.to_unsigned(remainder)
        elif inst.opcode == 'REMU':
            # Unsigned remainder
            if rs2_val == 0:
                # Division by zero: return dividend
                result = rs1_val
            else:
                result = rs1_val % rs2_val
        else:
            raise VMError(
                f"Unknown R-type instruction: {inst.opcode}",
                cpu=self.cpu,
                memory=self.memory,
                instructions=self.instructions
            )
        
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
            raise VMError(
                f"Unknown I-type instruction: {inst.opcode}",
                cpu=self.cpu,
                memory=self.memory,
                instructions=self.instructions
            )
        
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
            raise VMError(
                f"Unknown S-type instruction: {inst.opcode}",
                cpu=self.cpu,
                memory=self.memory,
                instructions=self.instructions
            )
        
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
            raise VMError(
                f"Unknown B-type instruction: {inst.opcode}",
                cpu=self.cpu,
                memory=self.memory,
                instructions=self.instructions
            )
        
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
            raise VMError(
                f"Unknown J-type instruction: {inst.opcode}",
                cpu=self.cpu,
                memory=self.memory,
                instructions=self.instructions
            )
    
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
            raise VMError(
                f"Unknown U-type instruction: {inst.opcode}",
                cpu=self.cpu,
                memory=self.memory,
                instructions=self.instructions
            )
        
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
    
    def get_current_instruction(self):
        """
        Get the instruction at the current PC
        
        Returns:
            Instruction object or None if PC is out of bounds
        """
        # PC is byte address, instructions are stored sequentially
        index = self.cpu.pc // 4
        if 0 <= index < len(self.instructions):
            return self.instructions[index]
        return None
    
    def get_current_instruction_text(self):
        """
        Get human-readable text of instruction at current PC
        
        Returns:
            String representation of instruction or "???" if invalid
        """
        instruction = self.get_current_instruction()
        if instruction:
            return self._format_instruction(instruction)
        return "???"
    
    def get_next_instruction_text(self):
        """
        Get human-readable text of next instruction (at PC+4)
        
        For sequential flow, this shows the instruction that will execute next.
        For branches/jumps, this shows the sequential case (not taken/fallthrough).
        
        Returns:
            String representation of next instruction or appropriate message
        """
        if self.cpu.halted:
            return "(halted)"
        
        if self.cpu.waiting_for_interrupt:
            return "(waiting for interrupt)"
        
        # Get next sequential instruction at PC+4
        next_pc = self.cpu.pc + 4
        next_instruction = self.get_instruction_at_address(next_pc)
        
        if next_instruction:
            return self._format_instruction(next_instruction)
        
        return "(end of program)"
    
    def get_instruction_at_address(self, address):
        """
        Get instruction at a specific address
        
        Args:
            address: Memory address (byte address)
            
        Returns:
            Instruction object or None
        """
        index = address // 4
        if 0 <= index < len(self.instructions):
            return self.instructions[index]
        return None
    
    def _format_instruction(self, inst):
        """
        Format an instruction as human-readable text
        
        Args:
            inst: Instruction object
            
        Returns:
            Formatted string like "ADDI x5, x5, 1"
        """
        opcode = inst.opcode
        
        # Handle different instruction formats
        if inst.type == InstructionType.R_TYPE:
            return f"{opcode} x{inst.rd}, x{inst.rs1}, x{inst.rs2}"
        
        elif inst.type == InstructionType.I_TYPE:
            if opcode in ['LW', 'LB', 'LH', 'LBU', 'LHU']:
                # Load: rd, offset(rs1)
                return f"{opcode} x{inst.rd}, {inst.imm}(x{inst.rs1})"
            elif opcode in ['JALR']:
                return f"{opcode} x{inst.rd}, {inst.imm}(x{inst.rs1})"
            elif opcode.startswith('CSR'):
                # CSR instructions
                return f"{opcode} x{inst.rd}, 0x{inst.imm:03X}, x{inst.rs1}"
            else:
                # Regular I-type: rd, rs1, imm
                return f"{opcode} x{inst.rd}, x{inst.rs1}, {inst.imm}"
        
        elif inst.type == InstructionType.S_TYPE:
            # Store: rs2, offset(rs1)
            return f"{opcode} x{inst.rs2}, {inst.imm}(x{inst.rs1})"
        
        elif inst.type == InstructionType.B_TYPE:
            # Branch: rs1, rs2, offset
            target = self.cpu.pc + inst.imm
            return f"{opcode} x{inst.rs1}, x{inst.rs2}, 0x{target:X} ({inst.imm:+d})"
        
        elif inst.type == InstructionType.J_TYPE:
            if opcode == 'JAL':
                target = self.cpu.pc + inst.imm
                return f"{opcode} x{inst.rd}, 0x{target:X} ({inst.imm:+d})"
            else:
                return f"{opcode} x{inst.rd}, {inst.imm}(x{inst.rs1})"
        
        elif inst.type == InstructionType.U_TYPE:
            return f"{opcode} x{inst.rd}, 0x{inst.imm:X}"
        
        elif inst.type == InstructionType.HALT:
            return opcode
        
        return str(inst)
