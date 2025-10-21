# CPU Visualization Feature

## Overview

The RISC VM includes a powerful CPU state visualization feature that displays CPU registers, control/status registers (CSRs), and execution state alongside the memory-mapped display. This feature is designed to help you understand how the CPU works and how assembly instructions affect the system state.

## Features

### 1. **Visual Step Mode**
Step through your program instruction by instruction while seeing:
- Current program counter (PC)
- All 32 general-purpose registers with ABI names (zero, ra, sp, a0-a7, s0-s11, t0-t6)
- CPU status (RUNNING, WFI, HALTED)
- Next instruction to be executed
- Control and Status Registers (mstatus, mie, mip, mtvec)
- Changed registers highlighted in yellow
- Decoded CSR flags

### 2. **Live Mode with CPU View**
Watch your program execute in real-time with periodic updates showing:
- Display output
- CPU register state
- Execution statistics

### 3. **Side-by-Side Layout**
Display and CPU state panels are shown side by side for easy comparison and monitoring.

## Usage

### Step Mode with CPU View

```bash
# Basic step mode with CPU visualization
uv run python main.py -s --cpu-view examples/hello.asm

# Or using the convenience script
./run.sh -s --cpu-view examples/fibonacci.asm
```

**Commands in step mode:**
- `s` or `Enter` - Step (execute next instruction)
- `c` - Continue (run continuously until halt)
- `r` - Show detailed register dump
- `d` - Show display only
- `m <addr>` - Show memory at address (hex or decimal)
- `b <addr>` - Set breakpoint at address (future feature)
- `q` - Quit

### Live Mode with CPU View

```bash
# Live display with CPU state updates
uv run python main.py -l --cpu-view --update-interval 1000 examples/clock.asm
```

### Terminal Width Requirements

The CPU visualization requires a minimum terminal width for the split-screen view:
- **Minimum:** 140 columns (default)
- **Recommended:** 150+ columns for comfortable viewing

If your terminal is too narrow, the feature will automatically fall back to display-only mode with a warning.

You can adjust the minimum width requirement:
```bash
uv run python main.py -s --cpu-view --min-width 120 examples/hello.asm
```

## Examples

### Example 1: Learning Basic Instructions

```bash
# Step through hello.asm to see how characters are written to display
uv run python main.py -s --cpu-view examples/hello.asm
```

Watch how:
- LUI loads the display base address into x10
- ADDI sets character codes in x11
- SW writes characters to memory-mapped display
- Registers change with each instruction (highlighted in yellow)

### Example 2: Understanding Interrupts

```bash
# Step through the timer example to see interrupt handling
uv run python main.py -s --cpu-view examples/timer_test.asm
```

Observe:
- CSR registers (mstatus, mie, mtvec) being configured
- WFI state when CPU waits for interrupts
- Interrupt pending bits in mip
- PC jumping to interrupt handler

### Example 3: Live Clock Demo

```bash
# Watch the clock run with real-time CPU state
uv run python main.py -l --cpu-view --update-interval 5000 examples/clock.asm
```

See:
- Real-time timer interrupts
- Register values changing (x20=hours, x21=minutes, x22=seconds)
- Display updating with formatted time

## Technical Details

### Register Display Format

Registers are shown with ABI names for easier identification:
```
zero: 0x00000000  ra: 0x00000040
sp:   0x000BFFFC  gp: 0x00000000
t0:   0x00000048  t1: 0x00000065
a0:   0x000F0000  a1: 0x00000000
...
```

**Changed registers** are highlighted in yellow to help you track modifications.

### CSR Decoding

Control and Status Registers are shown with decoded flags:
```
mstatus: 0x00000008 [MIE:1]
mie:     0x00000880 [RTIE MTIE]
mip:     0x00000000 [none]
mtvec:   0x00000100
```

- **mstatus**: Machine status with MIE (Machine Interrupt Enable) bit
- **mie**: Interrupt enable bits (MTIE=cycle timer, RTIE=real-time timer)
- **mip**: Interrupt pending bits
- **mtvec**: Trap vector base address

### CPU Status States

- **RUNNING**: Normal execution
- **WFI (waiting)**: CPU is in wait-for-interrupt state
- **HALTED**: Program has executed HALT instruction

## Implementation Details

The visualization is built on the `rich` library for terminal rendering:
- **CPUVisualizer**: Manages CPU state display and change tracking
- **VMVisualizer**: Coordinates display and CPU panels
- **Change tracking**: Compares state between renders to highlight changes

The architecture supports both step-by-step debugging and live execution modes with the same underlying visualization code.

## Tips

1. **Wider is Better**: Use a wide terminal (150+ columns) for the best experience
2. **Step Through Slowly**: Take time to observe register changes in step mode
3. **Watch CSRs**: Pay special attention to CSR changes when learning interrupts
4. **Use Continue**: In step mode, use 'c' to run continuously after stepping through setup code
5. **Combine with Debug**: Use `-d` flag for even more detailed logging

## Troubleshooting

**"Terminal width too narrow" warning:**
- Resize your terminal window
- Use a terminal emulator that supports wide windows (iTerm2, Windows Terminal, etc.)
- Reduce the min-width requirement if needed (not recommended below 130 cols)

**Colors not showing:**
- Ensure your terminal supports ANSI colors
- Try a modern terminal emulator
- Check that `TERM` environment variable is set correctly

**Step mode not showing CPU panel:**
- Check terminal width
- Try explicitly adding `--cpu-view` flag
- Check for error messages on startup

## Future Enhancements

Planned features:
- Memory/stack visualization panel (3-column layout)
- Breakpoint support (partially implemented)
- Call stack visualization
- Instruction history (last N instructions)
- Reverse step (step backwards)
- Interactive register editing
- Full TUI mode with keyboard shortcuts

## Feedback

This is a new feature designed to enhance the learning experience. Feedback and suggestions are welcome!
