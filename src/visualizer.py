"""
Unified Visualizer for RISC VM
Coordinates display and CPU panels for both live and step modes
"""

import shutil
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from rich.layout import Layout
from rich import box

from .cpu_visualizer import CPUVisualizer


class VMVisualizer:
    """
    Unified visualization controller for the VM
    Works in both live mode and step mode
    """
    
    def __init__(self, vm, show_cpu=True, min_width=140):
        """
        Initialize visualizer
        
        Args:
            vm: VirtualMachine instance
            show_cpu: Whether to show CPU state panel
            min_width: Minimum terminal width for split view
        """
        self.vm = vm
        self.show_cpu = show_cpu
        self.min_width = min_width
        self.console = Console()
        self.cpu_viz = CPUVisualizer()
        
        # Check terminal width
        self.terminal_width = shutil.get_terminal_size().columns
        self.can_show_split = self.terminal_width >= min_width
        
    def render(self, show_instructions=True, clear_screen=True):
        """
        Render VM state (display + optional CPU panel)
        
        Args:
            show_instructions: Show current and next instructions in CPU panel
            clear_screen: Whether to clear screen before rendering
        """
        if clear_screen:
            self.console.clear()
        
        # Update CPU change tracking
        self.cpu_viz.update_and_track_changes(self.vm.cpu)
        
        if not self.show_cpu or not self.can_show_split:
            # Display only mode
            self._render_display_only()
        else:
            # Split view: display + CPU
            current_instr = None
            next_instr = None
            if show_instructions:
                current_instr = self.vm.get_current_instruction_text()
                next_instr = self.vm.get_next_instruction_text()
            
            self._render_split_view(current_instr, next_instr)
    
    def _render_display_only(self):
        """Render display panel only"""
        display_content = self.vm.display.get_text()
        panel = Panel(
            display_content,
            title="[bold]Display (80x25)[/bold]",
            border_style="green",
            box=box.ROUNDED,
            width=84  # 80 + borders
        )
        self.console.print(panel)
    
    def _render_split_view(self, current_instruction=None, next_instruction=None):
        """
        Render split view with display and CPU panels
        
        Args:
            current_instruction: Text of current instruction being executed
            next_instruction: Text of next instruction to execute
        """
        # Get display content
        display_content = self.vm.display.get_text()
        display_panel = Panel(
            display_content,
            title="[bold]Display (80x25)[/bold]",
            border_style="green",
            box=box.ROUNDED,
            width=84  # 80 + borders
        )
        
        # Get CPU panel
        cpu_panel = self.cpu_viz.render_panel(
            self.vm.cpu,
            show_current_instruction=current_instruction,
            show_next_instruction=next_instruction,
            compact=False
        )
        
        # Render side by side
        columns = Columns([display_panel, cpu_panel], equal=False, expand=False)
        self.console.print(columns)
    
    def render_step_mode(self, show_commands=True):
        """
        Render for step mode with command prompt
        
        Args:
            show_commands: Whether to show available commands
        """
        # Render main panels
        self.render(show_instructions=True, clear_screen=True)
        
        # Show commands
        if show_commands:
            self.console.print()
            commands = (
                "[bold cyan]Commands:[/bold cyan] "
                "[s]tep  [c]ontinue  [r]egisters  [d]isplay  "
                "[m]emory <addr>  [b]reak <addr>  [q]uit"
            )
            self.console.print(commands)
    
    def render_live_mode_update(self, instruction_count):
        """
        Render update for live mode (continuous execution)
        
        Args:
            instruction_count: Current instruction count
        """
        # Clear screen and render main panels (for in-place updates)
        self.render(show_instructions=False, clear_screen=True)
        
        # Show execution stats
        self.console.print()
        self.console.print(f"[bold]Instructions:[/bold] {instruction_count:,}", style="cyan")
    
    def print_message(self, message, style=""):
        """
        Print a message to console
        
        Args:
            message: Message to print
            style: Rich style string
        """
        self.console.print(message, style=style)
    
    def print_error(self, message):
        """Print an error message"""
        self.console.print(f"[bold red]Error:[/bold red] {message}")
    
    def print_warning(self, message):
        """Print a warning message"""
        self.console.print(f"[bold yellow]Warning:[/bold yellow] {message}")
    
    def print_info(self, message):
        """Print an info message"""
        self.console.print(f"[bold cyan]Info:[/bold cyan] {message}")
    
    def check_terminal_width(self):
        """
        Check if terminal is wide enough for split view
        
        Returns:
            Tuple of (is_wide_enough, current_width, min_width)
        """
        current = shutil.get_terminal_size().columns
        return (current >= self.min_width, current, self.min_width)
    
    def print_terminal_warning(self):
        """Print warning if terminal is too narrow"""
        is_wide, current, min_width = self.check_terminal_width()
        if not is_wide:
            self.print_warning(
                f"Terminal width ({current} cols) is below recommended minimum "
                f"({min_width} cols) for split view. CPU panel disabled."
            )
            self.print_info("Resize your terminal or use a larger window for full experience.")
            return True
        return False
