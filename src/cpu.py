"""
CPU module for the RISC VM
Implements 32-bit RISC processor with 32 general-purpose registers
"""

import logging

logger = logging.getLogger(__name__)

class CPU:
    """
    32-bit RISC CPU with:
    - 32 general-purpose registers (x0-x31)
    - Program counter (PC)
    - Control and Status Registers (CSRs) for interrupt handling
    - x0 is hardwired to zero
    """
    
    NUM_REGISTERS = 32
    
    # CSR addresses (RISC-V standard)
    CSR_MSTATUS = 0x300  # Machine status register
    CSR_MIE = 0x304      # Machine interrupt enable
    CSR_MTVEC = 0x305    # Machine trap vector base address
    CSR_MEPC = 0x341     # Machine exception program counter
    CSR_MCAUSE = 0x342   # Machine trap cause
    CSR_MIP = 0x344      # Machine interrupt pending
    
    # Interrupt/Exception codes
    INT_TIMER = 0x80000007       # Machine cycle-based timer interrupt
    INT_TIMER_REALTIME = 0x8000000B  # Machine real-time timer interrupt
    
    # mstatus bits
    MSTATUS_MIE = 0x08  # Machine interrupt enable bit
    
    # mie/mip bits
    MIE_MTIE = 0x80      # Machine timer interrupt enable bit (cycle-based)
    MIE_RTIE = 0x800     # Real-time timer interrupt enable bit
    
    def __init__(self):
        """Initialize CPU with registers and PC"""
        self.registers = [0] * self.NUM_REGISTERS
        self.pc = 0  # Program counter
        self.halted = False
        self.waiting_for_interrupt = False  # WFI state
        self.instruction_count = 0
        
        # Control and Status Registers
        self.csr = {
            self.CSR_MSTATUS: 0,  # Interrupts disabled by default
            self.CSR_MIE: 0,      # No interrupts enabled
            self.CSR_MTVEC: 0,    # Trap vector at 0x0
            self.CSR_MEPC: 0,     # Exception PC
            self.CSR_MCAUSE: 0,   # Trap cause
            self.CSR_MIP: 0,      # No interrupts pending
        }
        self.interrupt_enabled = False
    
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
        self.waiting_for_interrupt = False
        self.instruction_count = 0
        
        # Reset CSRs
        self.csr = {
            self.CSR_MSTATUS: 0,
            self.CSR_MIE: 0,
            self.CSR_MTVEC: 0,
            self.CSR_MEPC: 0,
            self.CSR_MCAUSE: 0,
            self.CSR_MIP: 0,
        }
        self.interrupt_enabled = False
    
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
    
    # CSR Operations
    
    def read_csr(self, csr_addr):
        """
        Read a CSR register
        
        Args:
            csr_addr: CSR address (12-bit)
            
        Returns:
            32-bit CSR value
        """
        if csr_addr not in self.csr:
            raise ValueError(f"Invalid CSR address: 0x{csr_addr:03X}")
        return self.csr[csr_addr]
    
    def write_csr(self, csr_addr, value):
        """
        Write a CSR register
        
        Args:
            csr_addr: CSR address (12-bit)
            value: 32-bit value to write
        """
        if csr_addr not in self.csr:
            raise ValueError(f"Invalid CSR address: 0x{csr_addr:03X}")
        
        self.csr[csr_addr] = value & 0xFFFFFFFF
        
        # Update interrupt_enabled flag based on mstatus
        if csr_addr == self.CSR_MSTATUS:
            self.interrupt_enabled = bool(value & self.MSTATUS_MIE)
            logger.debug(f"write_csr: mstatus=0x{value:08X}, MIE bit={value & self.MSTATUS_MIE}, interrupt_enabled={self.interrupt_enabled}")
    
    def set_csr_bits(self, csr_addr, mask):
        """
        Set bits in a CSR register (atomic read-modify-write)
        
        Args:
            csr_addr: CSR address
            mask: Bits to set
            
        Returns:
            Old value before modification
        """
        old_value = self.read_csr(csr_addr)
        new_value = old_value | mask
        self.write_csr(csr_addr, new_value)
        return old_value
    
    def clear_csr_bits(self, csr_addr, mask):
        """
        Clear bits in a CSR register (atomic read-modify-write)
        
        Args:
            csr_addr: CSR address
            mask: Bits to clear
            
        Returns:
            Old value before modification
        """
        old_value = self.read_csr(csr_addr)
        new_value = old_value & ~mask
        self.write_csr(csr_addr, new_value)
        return old_value
    
    # Interrupt Handling
    
    def enable_interrupts(self):
        """Enable interrupts globally"""
        self.csr[self.CSR_MSTATUS] |= self.MSTATUS_MIE
        self.interrupt_enabled = True
        logger.debug(f"enable_interrupts: mstatus now=0x{self.csr[self.CSR_MSTATUS]:08X}, interrupt_enabled={self.interrupt_enabled}")
    
    def disable_interrupts(self):
        """Disable interrupts globally"""
        self.csr[self.CSR_MSTATUS] &= ~self.MSTATUS_MIE
        self.interrupt_enabled = False
        logger.debug(f"disable_interrupts: mstatus now=0x{self.csr[self.CSR_MSTATUS]:08X}, interrupt_enabled={self.interrupt_enabled}")
    
    def set_interrupt_pending(self, interrupt_bit):
        """
        Set interrupt pending bit in MIP
        
        Args:
            interrupt_bit: Bit mask for interrupt type (e.g., MIE_MTIE for timer)
        """
        self.csr[self.CSR_MIP] |= interrupt_bit
    
    def clear_interrupt_pending(self, interrupt_bit):
        """
        Clear interrupt pending bit in MIP
        
        Args:
            interrupt_bit: Bit mask for interrupt type
        """
        self.csr[self.CSR_MIP] &= ~interrupt_bit
    
    def has_pending_interrupts(self):
        """
        Check if there are any pending and enabled interrupts
        
        Returns:
            True if interrupts should be taken
        """
        if not self.interrupt_enabled:
            return False
        
        # Check if any enabled interrupts are pending
        enabled = self.csr[self.CSR_MIE]
        pending = self.csr[self.CSR_MIP]
        
        result = bool(enabled & pending)
        # Debug: Log if waiting and interrupt pending
        if self.waiting_for_interrupt and pending:
            logger.debug(f"has_pending: enabled=0x{enabled:08X}, pending=0x{pending:08X}, result={result}")
        
        return result
    
    def get_highest_priority_interrupt(self):
        """
        Get the highest priority pending interrupt
        
        Priority order (highest to lowest):
        1. Real-time timer (external/time-based)
        2. Cycle-based timer (internal)
        
        Returns:
            Interrupt code or None if no interrupts pending
        """
        if not self.has_pending_interrupts():
            return None
        
        enabled = self.csr[self.CSR_MIE]
        pending = self.csr[self.CSR_MIP]
        active = enabled & pending
        
        # Check real-time timer interrupt first (higher priority)
        if active & self.MIE_RTIE:
            return self.INT_TIMER_REALTIME
        
        # Check cycle-based timer interrupt
        if active & self.MIE_MTIE:
            return self.INT_TIMER
        
        return None
    
    def enter_interrupt(self, cause):
        """
        Enter interrupt handler
        
        Args:
            cause: Interrupt cause code
        """
        logger.debug(f"enter_interrupt: cause=0x{cause:08X}, pc=0x{self.pc:08X}, mtvec=0x{self.csr[self.CSR_MTVEC]:08X}")
        # Save current PC to mepc
        self.csr[self.CSR_MEPC] = self.pc
        
        # Save cause
        self.csr[self.CSR_MCAUSE] = cause
        
        # Disable interrupts
        self.disable_interrupts()
        
        # Jump to trap vector
        self.pc = self.csr[self.CSR_MTVEC] & 0xFFFFFFFF
        logger.debug(f"enter_interrupt: jumped to handler at PC=0x{self.pc:08X}")
    
    def return_from_interrupt(self):
        """
        Return from interrupt handler (MRET instruction)
        """
        # Restore PC from mepc
        self.pc = self.csr[self.CSR_MEPC]
        
        # Re-enable interrupts
        self.enable_interrupts()
    
    def wait_for_interrupt(self):
        """
        Enter wait-for-interrupt state (WFI instruction)
        CPU will not execute instructions until an interrupt occurs
        """
        self.waiting_for_interrupt = True
    
    def wake_from_wait(self):
        """
        Wake CPU from wait-for-interrupt state
        Can be called by interrupt handler or externally for debugging
        """
        self.waiting_for_interrupt = False
