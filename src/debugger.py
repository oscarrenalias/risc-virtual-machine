"""
Debugger module for the RISC VM
Provides comprehensive exception reporting and debugging utilities
"""

import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class CPUDebugger:
    """
    Debugger utility for generating detailed CPU state reports
    Used for exception reporting and troubleshooting
    """
    
    # Register ABI names (RISC-V convention)
    REGISTER_NAMES = {
        0: "zero", 1: "ra", 2: "sp", 3: "gp", 4: "tp",
        5: "t0", 6: "t1", 7: "t2",
        8: "s0/fp", 9: "s1",
        10: "a0", 11: "a1", 12: "a2", 13: "a3", 14: "a4", 15: "a5",
        16: "a6", 17: "a7",
        18: "s2", 19: "s3", 20: "s4", 21: "s5", 22: "s6", 23: "s7",
        24: "s8", 25: "s9", 26: "s10", 27: "s11",
        28: "t3", 29: "t4", 30: "t5", 31: "t6"
    }
    
    CSR_NAMES = {
        0x300: "MSTATUS",
        0x304: "MIE",
        0x305: "MTVEC",
        0x341: "MEPC",
        0x342: "MCAUSE",
        0x344: "MIP",
    }
    
    def __init__(self, cpu, memory, instructions=None):
        """
        Initialize debugger
        
        Args:
            cpu: CPU instance
            memory: Memory instance
            instructions: List of Instruction objects (optional)
        """
        self.cpu = cpu
        self.memory = memory
        self.instructions = instructions or []
    
    def dump_registers(self, columns=4) -> str:
        """
        Generate formatted register dump
        
        Args:
            columns: Number of columns to display registers in
            
        Returns:
            Formatted string with register values
        """
        lines = ["Register State:"]
        
        # Display registers in columns
        for i in range(0, 32, columns):
            row_parts = []
            for j in range(columns):
                reg_num = i + j
                if reg_num >= 32:
                    break
                
                value = self.cpu.registers[reg_num]
                reg_name = self.REGISTER_NAMES.get(reg_num, f"x{reg_num}")
                signed_val = self.cpu.to_signed(value)
                
                # Format: x0 (zero): 0x00000000 (0)
                row_parts.append(
                    f"x{reg_num:2d} ({reg_name:5s}): 0x{value:08X} ({signed_val:11d})"
                )
            
            lines.append("  " + " | ".join(row_parts))
        
        # Add PC and instruction count
        lines.append("")
        lines.append(f"PC: 0x{self.cpu.pc:08X} ({self.cpu.pc})")
        lines.append(f"Instructions executed: {self.cpu.instruction_count}")
        lines.append(f"CPU halted: {self.cpu.halted}")
        lines.append(f"Waiting for interrupt: {self.cpu.waiting_for_interrupt}")
        
        return "\n".join(lines)
    
    def dump_csrs(self) -> str:
        """
        Generate formatted CSR (Control and Status Register) dump
        
        Returns:
            Formatted string with CSR values
        """
        lines = ["Control and Status Registers (CSRs):"]
        
        for addr, name in self.CSR_NAMES.items():
            if addr in self.cpu.csr:
                value = self.cpu.csr[addr]
                lines.append(f"  {name:8s} (0x{addr:03X}): 0x{value:08X}")
                
                # Add interpretations for specific CSRs
                if addr == self.cpu.CSR_MSTATUS:
                    mie = "ENABLED" if (value & self.cpu.MSTATUS_MIE) else "DISABLED"
                    lines.append(f"           └─ MIE (Machine Interrupt Enable): {mie}")
                
                elif addr == self.cpu.CSR_MIE:
                    mtie = "YES" if (value & self.cpu.MIE_MTIE) else "NO"
                    rtie = "YES" if (value & self.cpu.MIE_RTIE) else "NO"
                    lines.append(f"           ├─ MTIE (Cycle Timer Int Enable): {mtie}")
                    lines.append(f"           └─ RTIE (Real-time Timer Int Enable): {rtie}")
                
                elif addr == self.cpu.CSR_MIP:
                    mtip = "YES" if (value & self.cpu.MIE_MTIE) else "NO"
                    rtip = "YES" if (value & self.cpu.MIE_RTIE) else "NO"
                    lines.append(f"           ├─ MTIP (Cycle Timer Int Pending): {mtip}")
                    lines.append(f"           └─ RTIP (Real-time Timer Int Pending): {rtip}")
                
                elif addr == self.cpu.CSR_MCAUSE:
                    if value == self.cpu.INT_TIMER:
                        lines.append(f"           └─ Cause: Cycle-based Timer Interrupt")
                    elif value == self.cpu.INT_TIMER_REALTIME:
                        lines.append(f"           └─ Cause: Real-time Timer Interrupt")
                    elif value & 0x80000000:
                        lines.append(f"           └─ Cause: Interrupt (code: {value & 0x7FFFFFFF})")
                    else:
                        lines.append(f"           └─ Cause: Exception (code: {value})")
        
        lines.append("")
        lines.append(f"Global interrupts: {'ENABLED' if self.cpu.interrupt_enabled else 'DISABLED'}")
        
        return "\n".join(lines)
    
    def dump_stack(self, num_words=8) -> str:
        """
        Generate formatted stack dump
        
        Args:
            num_words: Number of 32-bit words to display from top of stack
            
        Returns:
            Formatted string with stack contents
        """
        lines = ["Stack State (grows down from 0xBFFFC):"]
        
        # Get stack pointer (x2)
        sp = self.cpu.registers[2]
        stack_top = 0xBFFFC
        stack_bottom = 0x80000
        
        # Calculate stack usage
        if sp > stack_top:
            lines.append(f"  WARNING: Stack pointer above stack region!")
            lines.append(f"  SP: 0x{sp:08X}")
        elif sp < stack_bottom:
            lines.append(f"  WARNING: Stack overflow! SP below stack region!")
            lines.append(f"  SP: 0x{sp:08X}")
        else:
            bytes_used = stack_top - sp + 4
            lines.append(f"  SP: 0x{sp:08X} ({bytes_used} bytes used of 256KB)")
        
        lines.append("")
        lines.append(f"  Top {num_words} words:")
        
        # Display stack contents
        try:
            for i in range(num_words):
                addr = sp + (i * 4)
                
                # Check if address is in valid stack range
                if addr < stack_bottom or addr > stack_top:
                    lines.append(f"    [0x{addr:08X}]: <out of stack range>")
                    continue
                
                try:
                    # Read word from memory
                    value = self.memory.read_word(addr)
                    signed_val = self.cpu.to_signed(value)
                    
                    # Mark current SP position
                    marker = "→ " if addr == sp else "  "
                    
                    lines.append(
                        f"  {marker}[0x{addr:08X}]: 0x{value:08X} ({signed_val:11d})"
                    )
                except Exception as e:
                    lines.append(f"    [0x{addr:08X}]: <read error: {e}>")
        except Exception as e:
            lines.append(f"  Error reading stack: {e}")
        
        return "\n".join(lines)
    
    def dump_instruction_context(self, window=2) -> str:
        """
        Show instruction context around current PC
        
        Args:
            window: Number of instructions before/after to show
            
        Returns:
            Formatted string with instruction context
        """
        lines = ["Instruction Context:"]
        
        if not self.instructions:
            lines.append("  (No instructions available)")
            return "\n".join(lines)
        
        # Calculate instruction index
        current_idx = self.cpu.pc // 4
        
        if current_idx < 0 or current_idx >= len(self.instructions):
            lines.append(f"  PC out of bounds: 0x{self.cpu.pc:08X}")
            return "\n".join(lines)
        
        # Show window of instructions
        start_idx = max(0, current_idx - window)
        end_idx = min(len(self.instructions), current_idx + window + 1)
        
        for idx in range(start_idx, end_idx):
            addr = idx * 4
            inst = self.instructions[idx]
            
            # Mark current instruction
            if idx == current_idx:
                marker = "→ "
                suffix = "  ← EXCEPTION HERE"
            else:
                marker = "  "
                suffix = ""
            
            lines.append(f"{marker}[0x{addr:04X}] {inst}{suffix}")
        
        return "\n".join(lines)
    
    def analyze_memory_region(self, address: int) -> str:
        """
        Identify which memory region an address belongs to
        
        Args:
            address: Memory address to analyze
            
        Returns:
            Formatted string with memory region info
        """
        lines = ["Memory Region Analysis:"]
        lines.append(f"  Address: 0x{address:08X}")
        lines.append("")
        
        # Determine region
        region_info = []
        
        if address < 0:
            region_info.append("  Status: INVALID (negative address)")
        elif address > 0xFFFFF:
            region_info.append("  Status: OUT OF BOUNDS (exceeds 1MB)")
            region_info.append(f"  Maximum valid address: 0xFFFFF")
        elif self.memory.TEXT_START <= address <= self.memory.TEXT_END:
            region_info.append("  Region: TEXT SEGMENT (program code)")
            region_info.append(f"  Range: 0x{self.memory.TEXT_START:05X} - 0x{self.memory.TEXT_END:05X} (64KB)")
            if self.memory.protect_text:
                region_info.append("  Protection: READ-ONLY")
        elif self.memory.DATA_START <= address <= self.memory.DATA_END:
            region_info.append("  Region: DATA SEGMENT (static/global data)")
            region_info.append(f"  Range: 0x{self.memory.DATA_START:05X} - 0x{self.memory.DATA_END:05X} (192KB)")
        elif self.memory.HEAP_START <= address <= self.memory.HEAP_END:
            region_info.append("  Region: HEAP (dynamic allocation)")
            region_info.append(f"  Range: 0x{self.memory.HEAP_START:05X} - 0x{self.memory.HEAP_END:05X} (256KB)")
        elif self.memory.STACK_END <= address <= self.memory.STACK_START:
            region_info.append("  Region: STACK (grows downward)")
            region_info.append(f"  Range: 0x{self.memory.STACK_END:05X} - 0x{self.memory.STACK_START:05X} (256KB)")
            sp = self.cpu.registers[2]
            if address > sp:
                region_info.append(f"  Note: Address is ABOVE current SP (0x{sp:08X})")
        elif self.memory.RAM_START <= address <= self.memory.RAM_END:
            region_info.append("  Region: GENERAL RAM")
            region_info.append(f"  Range: 0x{self.memory.RAM_START:05X} - 0x{self.memory.RAM_END:05X} (192KB)")
        elif self.memory.MMIO_START <= address <= self.memory.MMIO_END:
            region_info.append("  Region: MEMORY-MAPPED I/O")
            region_info.append(f"  Range: 0x{self.memory.MMIO_START:05X} - 0x{self.memory.MMIO_END:05X} (64KB)")
            
            # Identify specific MMIO device
            if self.memory.DISPLAY_BUFFER_START <= address <= self.memory.DISPLAY_BUFFER_END:
                region_info.append("  Device: Display Buffer")
            elif self.memory.DISPLAY_CONTROL_START <= address <= self.memory.DISPLAY_CONTROL_END:
                region_info.append("  Device: Display Control Registers")
            elif 0xF7E00 <= address <= 0xF7E1F:
                region_info.append("  Device: Cycle-based Timer Registers")
            elif 0xF7E20 <= address <= 0xF7E3F:
                region_info.append("  Device: Real-time Timer Registers")
        
        lines.extend(region_info)
        
        # Add memory map overview
        lines.append("")
        lines.append("Memory Layout:")
        lines.append("  0x00000 - 0x0FFFF: Text (64KB)")
        lines.append("  0x10000 - 0x3FFFF: Data (192KB)")
        lines.append("  0x40000 - 0x7FFFF: Heap (256KB)")
        lines.append("  0x80000 - 0xBFFFF: Stack (256KB, grows down)")
        lines.append("  0xC0000 - 0xEFFFF: RAM (192KB)")
        lines.append("  0xF0000 - 0xFFFFF: MMIO (64KB)")
        
        return "\n".join(lines)
    
    def dump_memory_around(self, address: int, num_lines=5, bytes_per_line=16) -> str:
        """
        Dump memory contents around a specific address
        
        Args:
            address: Center address
            num_lines: Number of lines to show (before and after)
            bytes_per_line: Bytes per line
            
        Returns:
            Formatted hexdump string
        """
        lines = [f"Memory dump around 0x{address:08X}:"]
        
        # Align to bytes_per_line boundary
        start_addr = (address - (num_lines * bytes_per_line // 2)) & ~(bytes_per_line - 1)
        end_addr = start_addr + (num_lines * bytes_per_line)
        
        try:
            for addr in range(start_addr, end_addr, bytes_per_line):
                # Read bytes
                hex_bytes = []
                ascii_chars = []
                
                for offset in range(bytes_per_line):
                    byte_addr = addr + offset
                    
                    try:
                        if 0 <= byte_addr < self.memory.SIZE:
                            byte_val = self.memory.read_byte(byte_addr)
                            hex_bytes.append(f"{byte_val:02X}")
                            # ASCII representation
                            if 32 <= byte_val <= 126:
                                ascii_chars.append(chr(byte_val))
                            else:
                                ascii_chars.append(".")
                        else:
                            hex_bytes.append("??")
                            ascii_chars.append("?")
                    except Exception:
                        hex_bytes.append("XX")
                        ascii_chars.append("X")
                
                # Mark the fault line
                marker = "→ " if start_addr <= address < addr + bytes_per_line else "  "
                
                # Format line
                hex_part = " ".join(hex_bytes)
                ascii_part = "".join(ascii_chars)
                lines.append(f"{marker}[0x{addr:08X}]: {hex_part}  |{ascii_part}|")
        
        except Exception as e:
            lines.append(f"  Error reading memory: {e}")
        
        return "\n".join(lines)
    
    def dump_interrupt_state(self) -> str:
        """
        Show interrupt and timer state
        
        Returns:
            Formatted string with interrupt/timer information
        """
        lines = ["Interrupt and Timer State:"]
        
        # Interrupt state
        lines.append(f"  Global interrupts: {'ENABLED' if self.cpu.interrupt_enabled else 'DISABLED'}")
        lines.append(f"  Waiting for interrupt: {'YES' if self.cpu.waiting_for_interrupt else 'NO'}")
        
        # Check for pending interrupts
        mip = self.cpu.csr.get(self.cpu.CSR_MIP, 0)
        mie = self.cpu.csr.get(self.cpu.CSR_MIE, 0)
        
        mtip = bool(mip & self.cpu.MIE_MTIE)
        rtip = bool(mip & self.cpu.MIE_RTIE)
        mtie = bool(mie & self.cpu.MIE_MTIE)
        rtie = bool(mie & self.cpu.MIE_RTIE)
        
        lines.append("")
        lines.append("  Interrupt Pending:")
        lines.append(f"    Cycle Timer (MTIP): {'YES' if mtip else 'NO'}")
        lines.append(f"    Real-time Timer (RTIP): {'YES' if rtip else 'NO'}")
        
        lines.append("")
        lines.append("  Interrupt Enabled:")
        lines.append(f"    Cycle Timer (MTIE): {'YES' if mtie else 'NO'}")
        lines.append(f"    Real-time Timer (RTIE): {'YES' if rtie else 'NO'}")
        
        # Timer state (if available)
        if hasattr(self.memory, 'timer') and self.memory.timer:
            timer = self.memory.timer
            lines.append("")
            lines.append("  Cycle-based Timer:")
            lines.append(f"    Counter: {timer.counter}")
            lines.append(f"    Compare: {timer.compare}")
            lines.append(f"    Control: 0x{timer.control:02X}")
            lines.append(f"    Enabled: {'YES' if (timer.control & 0x01) else 'NO'}")
            lines.append(f"    Prescaler: {timer.prescaler}")
        
        if hasattr(self.memory, 'rt_timer') and self.memory.rt_timer:
            rt_timer = self.memory.rt_timer
            lines.append("")
            lines.append("  Real-time Timer:")
            enabled = bool(rt_timer.control & 0x01)  # CTRL_ENABLE bit
            lines.append(f"    Enabled: {'YES' if enabled else 'NO'}")
            lines.append(f"    Frequency: {rt_timer.frequency} Hz")
            lines.append(f"    Compare: {rt_timer.compare}")
            lines.append(f"    Control: 0x{rt_timer.control:02X}")
            if enabled and rt_timer.frequency > 0:
                interval_ms = 1000.0 / rt_timer.frequency
                lines.append(f"    Interval: {interval_ms:.2f} ms")
        
        return "\n".join(lines)
    
    def classify_exception(self, exception: Exception) -> Dict[str, Any]:
        """
        Classify exception and extract relevant information
        
        Args:
            exception: The exception that occurred
            
        Returns:
            Dictionary with exception classification and details
        """
        from .memory import MemoryAccessError, MemoryProtectionError
        from .vm import VMError
        
        exc_type = type(exception).__name__
        
        # Get exception message carefully (VMError might not have detailed_report yet)
        try:
            exc_msg = super(Exception, exception).__str__() if isinstance(exception, VMError) else str(exception)
        except Exception:
            exc_msg = repr(exception)
        
        classification = {
            "type": exc_type,
            "message": exc_msg,
            "category": "Unknown",
            "hints": []
        }
        
        # Classify by exception type
        if isinstance(exception, MemoryAccessError):
            classification["category"] = "Memory Access Violation"
            
            if "out of bounds" in exc_msg.lower():
                classification["hints"].append("Address is outside valid memory range (0x00000 - 0xFFFFF)")
            if "unaligned" in exc_msg.lower():
                classification["hints"].append("Memory access must be aligned (4-byte for words, 2-byte for halfwords)")
            
        elif isinstance(exception, MemoryProtectionError):
            classification["category"] = "Memory Protection Violation"
            classification["hints"].append("Attempting to write to read-only memory (text segment)")
            classification["hints"].append("Check if you're accidentally writing to code addresses")
            
        elif isinstance(exception, ValueError):
            classification["category"] = "Invalid Value"
            
            if "register" in exc_msg.lower():
                classification["hints"].append("Register number must be 0-31 (x0-x31)")
            if "csr" in exc_msg.lower():
                classification["hints"].append("Invalid CSR address")
                
        elif isinstance(exception, VMError):
            classification["category"] = "VM Execution Error"
            
            if "pc out of bounds" in exc_msg.lower():
                classification["hints"].append("Program counter jumped to invalid instruction address")
                classification["hints"].append("Check for incorrect branch/jump targets")
            if "unknown instruction" in exc_msg.lower():
                classification["hints"].append("Instruction type not recognized")
                
        elif isinstance(exception, ZeroDivisionError):
            classification["category"] = "Division by Zero"
            classification["hints"].append("DIV/DIVU operation with zero divisor (handled per RISC-V spec)")
        
        return classification


def format_exception_report(cpu, memory, instructions, exception: Exception, 
                            fault_address: Optional[int] = None) -> str:
    """
    Generate comprehensive exception report
    
    Args:
        cpu: CPU instance
        memory: Memory instance
        instructions: List of instructions
        exception: The exception that occurred
        fault_address: Optional memory address that caused the fault
        
    Returns:
        Formatted exception report string
    """
    debugger = CPUDebugger(cpu, memory, instructions)
    
    lines = []
    lines.append("")
    lines.append("=" * 80)
    lines.append(" CPU EXCEPTION ".center(80, "="))
    lines.append("=" * 80)
    lines.append("")
    
    # Exception classification
    classification = debugger.classify_exception(exception)
    lines.append(f"Exception Type: {classification['type']}")
    lines.append(f"Category: {classification['category']}")
    lines.append(f"Message: {classification['message']}")
    
    if classification['hints']:
        lines.append("")
        lines.append("Hints:")
        for hint in classification['hints']:
            lines.append(f"  • {hint}")
    
    lines.append("")
    lines.append("-" * 80)
    lines.append("")
    
    # Instruction context
    lines.append(debugger.dump_instruction_context())
    lines.append("")
    lines.append("-" * 80)
    lines.append("")
    
    # Register dump
    lines.append(debugger.dump_registers())
    lines.append("")
    lines.append("-" * 80)
    lines.append("")
    
    # CSR dump
    lines.append(debugger.dump_csrs())
    lines.append("")
    lines.append("-" * 80)
    lines.append("")
    
    # Stack dump
    lines.append(debugger.dump_stack())
    lines.append("")
    lines.append("-" * 80)
    lines.append("")
    
    # Interrupt state
    lines.append(debugger.dump_interrupt_state())
    lines.append("")
    
    # Memory region analysis (if fault address provided)
    if fault_address is not None:
        lines.append("-" * 80)
        lines.append("")
        lines.append(debugger.analyze_memory_region(fault_address))
        lines.append("")
        lines.append("-" * 80)
        lines.append("")
        lines.append(debugger.dump_memory_around(fault_address))
        lines.append("")
    
    lines.append("=" * 80)
    
    return "\n".join(lines)
