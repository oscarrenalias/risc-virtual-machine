"""
CPU State Visualizer for RISC VM
Renders CPU registers, CSRs, and status with change tracking
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box


class CPUVisualizer:
    """
    Visualizes CPU state with change tracking and highlighting
    """
    
    def __init__(self):
        """Initialize CPU visualizer with change tracking"""
        self.console = Console()
        self.previous_registers = [0] * 32
        self.previous_pc = 0
        self.previous_csrs = {}
        self.previous_instruction_count = 0
        self.changed_registers = set()
        self.pc_changed = False
        
    def update_and_track_changes(self, cpu):
        """
        Update state and track what changed since last render
        
        Args:
            cpu: CPU instance to track
        """
        # Track PC changes
        self.pc_changed = (cpu.pc != self.previous_pc)
        
        # Track register changes
        self.changed_registers = {
            i for i in range(32) 
            if cpu.registers[i] != self.previous_registers[i]
        }
        
        # Store current state for next comparison
        self.previous_registers = cpu.registers.copy()
        self.previous_pc = cpu.pc
        self.previous_instruction_count = cpu.instruction_count
        self.previous_csrs = cpu.csr.copy()
    
    def render_to_string(self, cpu, show_next_instruction=None, compact=False):
        """
        Render CPU state to a string (for panel content)
        
        Args:
            cpu: CPU instance to render
            show_next_instruction: Optional instruction text to show
            compact: If True, use more compact rendering
            
        Returns:
            Formatted string with CPU state
        """
        lines = []
        
        # Program counter and status
        pc_style = "bold yellow" if self.pc_changed else "bold cyan"
        lines.append(f"[{pc_style}]PC:[/{pc_style}] [white]0x{cpu.pc:08X}[/white]")
        lines.append(f"[bold cyan]Instructions:[/bold cyan] [white]{cpu.instruction_count:,}[/white]")
        
        # CPU status
        if cpu.halted:
            lines.append(f"[bold red]Status:[/bold red] [red]HALTED[/red]")
        elif cpu.waiting_for_interrupt:
            lines.append(f"[bold yellow]Status:[/bold yellow] [yellow]WFI (waiting)[/yellow]")
        else:
            lines.append(f"[bold green]Status:[/bold green] [green]RUNNING[/green]")
        
        # Show next instruction if provided
        if show_next_instruction:
            lines.append("")
            lines.append(f"[bold magenta]Next:[/bold magenta] [white]{show_next_instruction}[/white]")
        
        lines.append("")
        lines.append("[bold cyan]═══ Registers ═══[/bold cyan]")
        
        # Registers in compact 2-column format
        for i in range(0, 32, 2):
            reg_line = []
            for j in range(2):
                reg_num = i + j
                if reg_num < 32:
                    name = self._get_register_name(reg_num)
                    value = cpu.registers[reg_num]
                    
                    if reg_num in self.changed_registers:
                        reg_line.append(f"[yellow]{name:4s}:[/yellow] [bold yellow]0x{value:08X}[/bold yellow]")
                    else:
                        reg_line.append(f"[cyan]{name:4s}:[/cyan] [white]0x{value:08X}[/white]")
            
            lines.append("  ".join(reg_line))
        
        # CSRs (Control and Status Registers)
        if not compact:
            lines.append("")
            lines.append("[bold cyan]═══ CSRs ═══[/bold cyan]")
            
            csr_info = [
                (0x300, "mstatus", self._decode_mstatus(cpu.csr[0x300])),
                (0x304, "mie", self._decode_mie(cpu.csr[0x304])),
                (0x344, "mip", self._decode_mip(cpu.csr[0x344])),
                (0x305, "mtvec", f"0x{cpu.csr[0x305]:08X}"),
            ]
            
            for addr, name, decoded in csr_info:
                value = cpu.csr[addr]
                lines.append(f"[cyan]{name:8s}:[/cyan] [white]0x{value:08X}[/white] [dim]{decoded}[/dim]")
        
        return "\n".join(lines)
    
    def render_panel(self, cpu, show_next_instruction=None, compact=False, title="CPU State"):
        """
        Render CPU state as a Rich panel
        
        Args:
            cpu: CPU instance to render
            show_next_instruction: Optional instruction text to show
            compact: If True, use more compact rendering
            title: Panel title
            
        Returns:
            Rich Panel object
        """
        content = self.render_to_string(cpu, show_next_instruction, compact)
        return Panel(
            content,
            title=f"[bold]{title}[/bold]",
            border_style="cyan",
            box=box.ROUNDED
        )
    
    def _get_register_name(self, reg_num):
        """Get conventional name for register with ABI aliases"""
        # Use ABI names for common registers
        abi_names = {
            0: 'zero', 1: 'ra', 2: 'sp', 3: 'gp',
            4: 'tp', 5: 't0', 6: 't1', 7: 't2',
            8: 's0', 9: 's1', 10: 'a0', 11: 'a1',
            12: 'a2', 13: 'a3', 14: 'a4', 15: 'a5',
            16: 'a6', 17: 'a7', 18: 's2', 19: 's3',
            20: 's4', 21: 's5', 22: 's6', 23: 's7',
            24: 's8', 25: 's9', 26: 's10', 27: 's11',
            28: 't3', 29: 't4', 30: 't5', 31: 't6',
        }
        return abi_names.get(reg_num, f'x{reg_num}')
    
    def _decode_mstatus(self, value):
        """Decode mstatus register bits"""
        mie = bool(value & 0x08)
        return f"[MIE:{1 if mie else 0}]"
    
    def _decode_mie(self, value):
        """Decode MIE (interrupt enable) register"""
        bits = []
        if value & 0x80:   # MTIE
            bits.append("MTIE")
        if value & 0x800:  # RTIE
            bits.append("RTIE")
        return "[" + " ".join(bits) + "]" if bits else "[none]"
    
    def _decode_mip(self, value):
        """Decode MIP (interrupt pending) register"""
        bits = []
        if value & 0x80:   # MTIP
            bits.append("MTIP")
        if value & 0x800:  # RTIP
            bits.append("RTIP")
        return "[" + " ".join(bits) + "]" if bits else "[none]"
    
    def get_changed_registers_summary(self):
        """
        Get a summary of changed registers
        
        Returns:
            List of (reg_num, name, old_value, new_value) tuples
        """
        changes = []
        for reg_num in sorted(self.changed_registers):
            name = self._get_register_name(reg_num)
            # Note: We don't store old values, but this structure allows for future enhancement
            changes.append((reg_num, name))
        return changes
