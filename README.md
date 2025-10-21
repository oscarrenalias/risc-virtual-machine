# RISC Virtual Machine

[![Test Suite](https://github.com/oscarrenalias/risc-virtual-machine/actions/workflows/tests.yml/badge.svg)](https://github.com/oscarrenalias/risc-virtual-machine/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/badge/coverage-70%25-brightgreen.svg)](./TESTING.md)
[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A 32-bit RISC assembly interpreter written in Python with memory-mapped display output.

This is a pet project that I implemented over the weekend, for the fun of it, with the help of GitHub Copilot.

Implements a subset of the RISC-V instruction set, including 32 registers, 1024Mb of memory and a memory mapped areas to simulate a 80x25 screen. 

Several code examples are providedd in the ```examples``` folder to get started.

## Quick Start

```bash
# Run with UV (recommended)
uv run python main.py examples/hello.asm

# Or use the convenience script
./run.sh examples/hello.asm

# Try other examples
./run.sh examples/counter.asm
./run.sh examples/fibonacci.asm
./run.sh examples/test.asm

# Enable debug mode
./run.sh -d examples/counter.asm

# Control CPU speed (NEW!)
./run.sh examples/hello.asm --clock-hz 100     # 100 Hz (slow motion)
./run.sh examples/hello.asm --clock-hz 10000   # 10 kHz (fast)
./run.sh examples/hello.asm --no-clock         # Maximum speed

# Step through execution with CPU visualization (NEW!)
./run.sh -s --cpu-view examples/test.asm

# Live display with CPU state panel (NEW!)
./run.sh -l --cpu-view examples/clock.asm
```

## Features

- **32-bit RISC Architecture**: Based on RISC-V instruction set
- **32 General-Purpose Registers**: x0-x31 (x0 hardwired to zero)
- **Label Support**: Use labels directly in instructions instead of manual address calculation
- **Configurable CPU Clock**: Simulate real CPU execution speed (1 Hz - 10 kHz, or unlimited) (NEW!)
  - Default 1 kHz (1ms per instruction)
  - Educational tool for understanding code optimization impact
  - Can be disabled for maximum speed
  - See [CPU_CLOCK.md](docs/CPU_CLOCK.md) for details
- **1MB Memory**: 
  - Text segment (64KB)
  - Data segment (192KB)
  - Heap (256KB)
  - Stack (256KB)
  - Memory-mapped I/O (64KB)
- **Memory-Mapped Display**: 80x25 character text display
- **Comprehensive Instruction Set**: Arithmetic, logical, memory, branch, and jump instructions
- **Two Hardware Timers**: Cycle-based (deterministic) and real-time (wall-clock) timers
- **Interrupt Support**: Hardware interrupts with CSR-based control
- **Debug Mode**: Step-through execution with register inspection
- **CPU Visualization**: Real-time display of registers, CSRs, and execution state (NEW!)
  - Side-by-side display and CPU state panels
  - Change tracking with highlighted registers
  - Instruction preview
  - Works in both step and live modes
  - See [CPU_VISUALIZATION.md](docs/CPU_VISUALIZATION.md) for details

## Memory Layout

```
0x00000 - 0x0FFFF: Text segment (64KB)    - Program instructions
0x10000 - 0x3FFFF: Data segment (192KB)   - Static/global data
0x40000 - 0x7FFFF: Heap (256KB)           - Dynamic allocation
0x80000 - 0xBFFFF: Stack (256KB)          - Grows downward from 0xBFFFF
0xC0000 - 0xEFFFF: General RAM (192KB)    - Additional space
0xF0000 - 0xFFFFF: Memory-mapped I/O (64KB)
  0xF0000 - 0xF7CFF: Display buffer (80x25 characters)
  0xF7D00 - 0xF7D7F: Display control registers
  0xF7E00 - 0xF7E10: Cycle-based timer registers
  0xF7E20 - 0xF7E30: Real-time timer registers
```

## Timers and Interrupts

The VM includes TWO hardware timers that can generate periodic interrupts:

### 1. Cycle-Based Timer (Deterministic)

Instruction-cycle based timing for deterministic behavior and testing.

**Registers (Memory-Mapped):**
```
0xF7E00: TIMER_COUNTER   (R/W) - Current counter value
0xF7E04: TIMER_COMPARE   (R/W) - Interrupt threshold
0xF7E08: TIMER_CONTROL   (R/W) - Control register
0xF7E0C: TIMER_PRESCALER (R/W) - Clock divider
0xF7E10: TIMER_STATUS    (R)   - Status flags
```

**Control Register Bits:**
- Bit 0: **ENABLE** - Enable timer
- Bit 1: **MODE** - 0=one-shot, 1=periodic
- Bit 2: **INT_PENDING** - Interrupt pending (write 1 to clear)
- Bit 3: **AUTO_RELOAD** - Auto-reload counter in periodic mode

### 2. Real-Time Timer (Wall-Clock Based)

Wall-clock based timing for real-world event simulation (1 Hz - 1000 Hz).

**Registers (Memory-Mapped):**
```
0xF7E20: RT_TIMER_COUNTER   (R)   - Ticks since start
0xF7E24: RT_TIMER_FREQUENCY (R/W) - Frequency in Hz (1-1000)
0xF7E28: RT_TIMER_CONTROL   (R/W) - Control register
0xF7E2C: RT_TIMER_STATUS    (R)   - Status flags
0xF7E30: RT_TIMER_COMPARE   (R/W) - Alarm compare value
```

**Control Register Bits:**
- Bit 0: **ENABLE** - Enable timer
- Bit 1: **MODE** - 0=periodic, 1=one-shot
- Bit 2: **INT_PENDING** - Interrupt pending (write 1 to clear)
- Bit 3: **ALARM_MODE** - Use compare for alarm

### Control and Status Registers (CSRs)

```
0x300: mstatus  - Machine status (bit 3 = global interrupt enable)
0x304: mie      - Interrupt enable (bit 7 = cycle timer, bit 11 = RT timer)
0x305: mtvec    - Trap vector base address (interrupt handler)
0x341: mepc     - Exception PC (saved PC during interrupt)
0x342: mcause   - Trap cause (0x80000007 = cycle timer, 0x8000000B = RT timer)
0x344: mip      - Interrupt pending flags
```

### Interrupt Programming

**Cycle-Based Timer Example:**
1. Set up interrupt handler address in `mtvec`
2. Configure timer with compare value
3. Enable cycle timer interrupt in `mie` (bit 7 = 0x80)
4. Enable global interrupts in `mstatus` (bit 3 = 0x08)
5. Implement handler that clears pending bit and uses `MRET`

**Real-Time Timer Example:**
1. Set up interrupt handler address in `mtvec`
2. Configure RT timer frequency (1-1000 Hz)
3. Enable RT timer interrupt in `mie` (bit 11 = 0x800)
4. Enable global interrupts in `mstatus` (bit 3 = 0x08)
5. Implement handler that clears pending bit and uses `MRET`

**Examples:**
- `examples/timer_test.asm` - Cycle-based timer test
- `examples/rt_timer_test.asm` - Real-time timer test
- `examples/clock.asm` - Real-time clock using RT timer at 1 Hz

## Assembly Language

### Label Support

Labels can be used directly in instructions instead of manually calculating addresses:

```asm
# OLD WAY - Manual address calculation
LUI x1, 0x0
ADDI x1, x1, 380        # Must manually calculate handler address
CSRRW x0, 0x305, x1

# NEW WAY - Use labels directly
LUI x1, 0x0
ADDI x1, x1, timer_handler    # Assembler resolves automatically!
CSRRW x0, 0x305, x1

timer_handler:
    ADDI x3, x3, 1
    MRET
```

**Supported in:**
- I-type instructions: `ADDI`, `ANDI`, `ORI`, `XORI`, `SLTI`, `SLTIU`, etc.
- Branch instructions: `BEQ`, `BNE`, `BLT`, `BGE`, `BLTU`, `BGEU`
- Jump instructions: `JAL`

See [docs/LABEL_SUPPORT.md](docs/LABEL_SUPPORT.md) for detailed documentation.

**Examples:**
- `examples/label_demo.asm` - Simple label usage demonstration
- `examples/clock_with_labels.asm` - Clock example using label-based addressing

### Comments

```asm
# This is a comment
ADDI x1, x2, 10    # Inline comment
; Semicolons also work
```

## Instruction Set

The VM implements a subset of the RISC-V instruction set including:

- **Base Integer Instructions (RV32I)**: Arithmetic, logical, shift, memory, branch, jump
- **M-Extension (Multiply/Divide)**: MUL, DIV, DIVU, REM, REMU ✨ NEW
- **CSR Instructions**: Control and Status Register operations
- **Privileged Instructions**: MRET for interrupt handling

For the complete instruction set reference, see [docs/INSTRUCTION_SET.md](docs/INSTRUCTION_SET.md)

### Example Programs Using M-Extension

```bash
# Multiplication examples
./run.sh examples/multiply.asm

# Division and remainder examples
./run.sh examples/division.asm

# Prime number checker using MUL and REM
./run.sh examples/prime_check.asm
```

## Usage

### Basic Execution

With UV (recommended):
```bash
uv run python main.py examples/hello.asm
# Or use the convenience script:
./run.sh examples/hello.asm
```

### Debug Mode

```bash
uv run python main.py -d examples/fibonacci.asm
```

### Step-by-Step Execution

```bash
uv run python main.py -s examples/counter.asm
```

Commands in step mode:
- `[Enter]` - Execute next instruction
- `r` - Show registers
- `d` - Show display
- `m <addr>` - Show memory at address (hex)
- `q` - Quit

### Command-Line Options

```
usage: main.py [-h] [-d] [-s] [-p] [-m MAX_INSTRUCTIONS] [--no-display] file

positional arguments:
  file                  Assembly source file to execute

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Enable debug output
  -s, --step            Step through execution
  -p, --protect         Protect text segment from writes
  -m MAX_INSTRUCTIONS, --max-instructions MAX_INSTRUCTIONS
                        Maximum instructions to execute (default: 1000000)
  --no-display          Disable display rendering
```

## Example Programs

### Hello World (`examples/hello.asm`)
Displays "Hello, World!" using memory-mapped display.

### Counter (`examples/counter.asm`)
Counts from 0 to 9 and displays each number.

### Fibonacci (`examples/fibonacci.asm`)
Calculates and displays the first 10 Fibonacci numbers.

### Factorial (`examples/factorial.asm`)
Calculates 5! = 120.

### Test (`examples/test.asm`)
Tests various instruction types.

### Multiply (`examples/multiply.asm`) ✨ NEW
Demonstrates MUL instruction with power calculation (2^5 = 32).

### Division (`examples/division.asm`) ✨ NEW
Shows DIV, DIVU, REM, REMU instructions with signed/unsigned examples.

### Prime Check (`examples/prime_check.asm`) ✨ NEW
Prime number checker using MUL and REM instructions.

## Writing Assembly Programs

### Program Structure

```assembly
# Comments start with # or ;

.text                   # Code section
main:                   # Label
    ADDI x1, x0, 10    # Instruction
    HALT               # Stop execution

.data                   # Data section (optional)
```

### Register Naming

Registers can be referenced by number or name:
- `x0-x31` - General purpose (x0 is always zero)
- `zero` - Alias for x0
- `ra` - Return address (x1)
- `sp` - Stack pointer (x2)
- `gp` - Global pointer (x3)
- `tp` - Thread pointer (x4)
- `fp` or `s0` - Frame pointer (x8)

### Number Formats

```assembly
ADDI x1, x0, 42        # Decimal
ADDI x1, x0, 0x2A      # Hexadecimal
ADDI x1, x0, 0b101010  # Binary
```

### Memory-Mapped Display

To write to the display:

```assembly
LUI x10, 0xF0          # Load display base address (0xF0000)
ADDI x11, x0, 65       # Load ASCII 'A' (65)
SW x11, 0(x10)         # Write to display
```

Display control registers:
- `0xF7D00`: Current page (0-15)
- `0xF7D01`: Cursor X position (0-79)
- `0xF7D02`: Cursor Y position (0-24)
- `0xF7D03`: Display mode
- `0xF7D04`: Scroll enable (0=no, 1=yes)
- `0xF7D05`: Clear screen (write any value)

## Architecture Details

### Registers

- All registers are 32-bit
- Register x0 is hardwired to zero (writes are ignored)
- Stack grows downward from 0xBFFFF
- Stack pointer (sp/x2) is initialized to 0xBFFFF

### Instruction Encoding

Instructions are stored as Python objects with:
- Opcode (mnemonic)
- Type (R/I/S/B/J/U)
- Operands (rd, rs1, rs2, immediate)

### Memory

- Byte-addressable with 32-bit word alignment for most operations
- Little-endian byte order
- Memory-mapped I/O for display output
- Optional text segment protection

### Program Counter

- PC increments by 4 bytes per instruction
- Branches and jumps modify PC directly
- PC starts at 0x00000

## Project Structure

```
assembly-virtual-machine/
├── src/
│   ├── cpu.py          # CPU with registers
│   ├── memory.py       # Memory management
│   ├── display.py      # Display rendering
│   ├── instruction.py  # Instruction definitions
│   ├── assembler.py    # Assembly parser
│   └── vm.py           # Virtual machine
├── examples/
│   ├── hello.asm       # Hello World
│   ├── counter.asm     # Counter program
│   ├── fibonacci.asm   # Fibonacci sequence
│   ├── factorial.asm   # Factorial calculator
│   └── test.asm        # Instruction tests
├── main.py             # CLI entry point
└── README.md           # This file
```

## Requirements

- Python 3.7 or higher
- UV package manager (recommended) or standard Python
- No external dependencies (uses only standard library)

## Installation

```bash
# Install UV if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone or navigate to the project directory
cd assembly-virtual-machine

# Initialize the project (already done)
uv sync
```

## Development

### Running Tests

The project has a comprehensive 3-layer test suite with **199 tests** and **70% code coverage**:

```bash
# Run all tests (unit + integration + program)
./run_tests.sh

# Run with coverage report
./run_tests.sh --coverage

# Run specific test layer
./run_tests.sh --test tests/unit/        # Unit tests only
./run_tests.sh --test tests/integration/ # Integration tests only
./run_tests.sh --test tests/programs/    # Program tests only

# Run verbose
./run_tests.sh -v

# Skip slow tests
./run_tests.sh --fast
```

**Test Layers:**
- **Layer 1 (Unit)**: 154 tests - Component isolation (CPU, Memory, Timer, etc.)
- **Layer 2 (Integration)**: 30 tests - Full VM instruction execution
- **Layer 3 (Program)**: 15 tests - Complete realistic programs (factorial, fibonacci, etc.)

See [TESTING.md](TESTING.md) for complete testing documentation.

### Continuous Integration

Every commit triggers automated testing via GitHub Actions:
- ✅ Full test suite (199 tests) runs on Ubuntu with Python 3.13
- ✅ Coverage threshold enforced (≥65%, currently 70%)
- ✅ Coverage reports uploaded as artifacts

View workflow results in the [Actions tab](https://github.com/oscarrenalias/risc-virtual-machine/actions).

### Adding New Instructions

1. Add to `INSTRUCTION_SET` in `instruction.py`
2. Implement execution logic in `vm.py`
3. Add unit tests in `tests/unit/`
4. Add integration test in `tests/integration/test_instructions.py`
5. Optionally add program test using the instruction

### Writing Tests

```python
# Unit test example
def test_cpu_register(cpu):
    cpu.write_register(1, 42)
    assert cpu.read_register(1) == 42

# Integration test example  
def test_add_instruction(vm):
    program = """
    ADDI x1, x0, 10
    ADDI x2, x0, 20
    ADD x3, x1, x2
    HALT
    """
    result = run_and_get_register(vm, program, 3)
    assert result == 30

# Program test example
def test_factorial(vm):
    # Complete factorial program
    result = run_and_get_register(vm, program, 11)
    assert result == 120
```

See [tests/README.md](tests/README.md) and [docs/PROGRAM_TESTING.md](docs/PROGRAM_TESTING.md) for detailed guides.

## Future Enhancements

- [X] Multiply and divide instructions (MUL, DIV, DIVU, REM, REMU implemented)
- [ ] High multiply instructions (MULH, MULHSU, MULHU - Phase 3 of M-extension)
- [ ] Floating-point support
- [ ] System calls for I/O
- [ ] Graphics mode display
- [X] Interrupt handling
- [X] Text-based visualization
- [X] Step execution of instructions
- [ ] Debugger GUI
- [ ] Multiple display pages
- [ ] Color support
```