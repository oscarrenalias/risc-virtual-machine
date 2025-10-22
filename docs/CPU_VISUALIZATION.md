# Live Visualization Feature

## Overview

The RISC VM includes a powerful live visualization feature that displays both the memory-mapped display (80x25 text) and CPU state (registers, CSRs, execution state) side by side. This feature is designed to help you understand how the CPU works and how assembly instructions affect the system state.

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
- Display output in real-time

### 2. **Live Continuous Execution**
Watch your program execute in real-time with periodic updates showing:
- Display output
- CPU register state
- Execution statistics
- Automatic update intervals based on clock speed

### 3. **Side-by-Side Layout**
Display and CPU state panels are shown side by side for easy comparison and monitoring.

## Usage

### Step Mode with Visualization

```bash
# Step mode with full visualization (display + CPU state)
uv run python main.py -s -l examples/hello.asm

# Or using the convenience script
./run.sh -s -l examples/fibonacci.asm
```

### Live Continuous Execution

```bash
# Live visualization during continuous execution
uv run python main.py -l examples/clock.asm

# With specific clock speed for better viewing
uv run python main.py -l --clock-hz 5 examples/counter.asm
```

### Terminal Width Requirements

The CPU visualization requires a minimum terminal width for the split-screen view:
- **Minimum:** 140 columns (default)
- **Recommended:** 150+ columns for comfortable viewing

If your terminal is too narrow, the feature will automatically fall back to display-only mode with a warning.

You can adjust the minimum width requirement:
```bash
uv run python main.py -s -l --min-width 120 examples/hello.asm
```

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

# Help Command in Step Mode

## Overview

The step mode in the RISC Virtual Machine includes a built-in help command (`?`) that displays a comprehensive list of all available commands with descriptions and usage examples.

## Feature Description

When running the VM in step-by-step execution mode (with `-s` or `--step` flag), users can type `?` at the command prompt to display a formatted help table showing all available commands.

### Accessing Help

At the command prompt, type `?` and press Enter:
```
[0x00000000]> ?
```

This will display a formatted table with all available commands.

## Available Commands

The help system displays the following commands:

| Command | Description |
|---------|-------------|
| `?` | Show this help message |
| `s` or `Enter` | Step: execute one instruction |
| `c` | Continue: run continuously until halt or breakpoint |
| `r` | Show registers (detailed dump) |
| `d` | Show display output |
| `p` | Show program listing (all loaded instructions) |
| `m <addr>` | Show memory at address (hex or decimal) |
| `b <addr>` | Set breakpoint at address (placeholder) |
| `q` | Quit execution |

## Examples

The help command also provides examples for complex commands:

- `m 0x1000` - Show memory at address 0x1000 (hexadecimal)
- `m 4096` - Show memory at address 4096 (decimal)
- `b 0x100` - Set breakpoint at 0x100 (placeholder feature)

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
- Ensure you're using the `-l` flag
- Check for error messages on startup