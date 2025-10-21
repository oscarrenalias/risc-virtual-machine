# RISC Virtual Machine

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

# Step through execution
./run.sh -s examples/test.asm
```

## Features

- **32-bit RISC Architecture**: Based on RISC-V instruction set
- **32 General-Purpose Registers**: x0-x31 (x0 hardwired to zero)
- **Label Support**: Use labels directly in instructions instead of manual address calculation
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

### Arithmetic (R-type)
- `ADD rd, rs1, rs2` - Add
- `SUB rd, rs1, rs2` - Subtract
- `SLT rd, rs1, rs2` - Set less than (signed)
- `SLTU rd, rs1, rs2` - Set less than (unsigned)

### Arithmetic Immediate (I-type)
- `ADDI rd, rs1, imm` - Add immediate
- `SLTI rd, rs1, imm` - Set less than immediate
- `SLTIU rd, rs1, imm` - Set less than immediate unsigned

### Logical (R-type)
- `AND rd, rs1, rs2` - Bitwise AND
- `OR rd, rs1, rs2` - Bitwise OR
- `XOR rd, rs1, rs2` - Bitwise XOR

### Logical Immediate (I-type)
- `ANDI rd, rs1, imm` - AND immediate
- `ORI rd, rs1, imm` - OR immediate
- `XORI rd, rs1, imm` - XOR immediate

### Shift (R-type)
- `SLL rd, rs1, rs2` - Shift left logical
- `SRL rd, rs1, rs2` - Shift right logical
- `SRA rd, rs1, rs2` - Shift right arithmetic

### Shift Immediate (I-type)
- `SLLI rd, rs1, shamt` - Shift left logical immediate
- `SRLI rd, rs1, shamt` - Shift right logical immediate
- `SRAI rd, rs1, shamt` - Shift right arithmetic immediate

### Memory Load (I-type)
- `LW rd, offset(rs1)` - Load word
- `LH rd, offset(rs1)` - Load halfword
- `LB rd, offset(rs1)` - Load byte
- `LHU rd, offset(rs1)` - Load halfword unsigned
- `LBU rd, offset(rs1)` - Load byte unsigned

### Memory Store (S-type)
- `SW rs2, offset(rs1)` - Store word
- `SH rs2, offset(rs1)` - Store halfword
- `SB rs2, offset(rs1)` - Store byte

### Branch (B-type)
- `BEQ rs1, rs2, label` - Branch if equal
- `BNE rs1, rs2, label` - Branch if not equal
- `BLT rs1, rs2, label` - Branch if less than
- `BGE rs1, rs2, label` - Branch if greater or equal
- `BLTU rs1, rs2, label` - Branch if less than unsigned
- `BGEU rs1, rs2, label` - Branch if greater or equal unsigned

### Jump (J-type)
- `JAL rd, label` - Jump and link
- `JALR rd, rs1, offset` - Jump and link register

### Upper Immediate (U-type)
- `LUI rd, imm` - Load upper immediate
- `AUIPC rd, imm` - Add upper immediate to PC

### Control and Status Registers (CSR)
- `CSRRW rd, csr, rs1` - Atomic Read/Write CSR
- `CSRRS rd, csr, rs1` - Atomic Read and Set Bits in CSR
- `CSRRC rd, csr, rs1` - Atomic Read and Clear Bits in CSR
- `CSRRWI rd, csr, imm` - Read/Write CSR, immediate
- `CSRRSI rd, csr, imm` - Read and Set Bits in CSR, immediate
- `CSRRCI rd, csr, imm` - Read and Clear Bits in CSR, immediate

### System
- `HALT` - Halt execution
- `MRET` - Return from interrupt/exception
- `NOP` - No operation

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

Create unit tests for individual components:

```python
from vm import VirtualMachine

vm = VirtualMachine()
vm.load_program("""
ADDI x1, x0, 42
HALT
""")
vm.run()
assert vm.cpu.read_register(1) == 42
```

### Adding New Instructions

1. Add to `INSTRUCTION_SET` in `instruction.py`
2. Implement execution logic in `vm.py`
3. Add test cases

## Future Enhancements

- [ ] Multiply and divide instructions
- [ ] Floating-point support
- [ ] System calls for I/O
- [ ] Graphics mode display
- [ ] Interrupt handling
- [ ] Debugger GUI
- [ ] Multiple display pages
- [ ] Color support