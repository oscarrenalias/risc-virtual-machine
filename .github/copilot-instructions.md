# GitHub Copilot Instructions

## Project Overview
This is a 32-bit RISC assembly interpreter written in Python that simulates a RISC-V-like instruction set with memory-mapped display output and various hardware features.

## Package Management
- **Always use `uv` for package management and running Python commands**
- Run Python scripts: `uv run python <script>.py`
- Run tests: `uv run pytest` or use `./run_tests.sh`
- Install dependencies: `uv pip install <package>`
- The project uses `pyproject.toml` for dependency management

## Key Concepts

### Architecture
- 32-bit RISC architecture based on RISC-V
- 32 general-purpose registers (x0-x31, x0 hardwired to zero)
- Full RISC-V ABI register name support (zero, ra, sp, gp, tp, t0-t6, s0-s11, a0-a7, fp)
  - Both x-notation and ABI names are supported
  - Can be used interchangeably in assembly code
  - Display shows both notations: "x10/a0"
- 1024MB memory (0x40000000 max)
- Memory-mapped regions:
  - Display: 0x10000000-0x100007CF (80x25 text)
  - Timer: 0x20000000 (control) + 0x20000004 (counter)
  - Realtime Timer: 0x30000000 (control) + 0x30000004 (counter)

### Instruction Set
- Arithmetic: ADD, SUB, MUL, DIV, MOD
- Logical: AND, OR, XOR, NOT, SHL, SHR
- Memory: LW (load word), SW (store word)
- Control: BEQ, BNE, BLT, BGE, JAL, JALR
- System: HALT, NOP, WFI (wait for interrupt)
- Interrupts: MRET (return from interrupt), MTIMECMP (timer compare)
- Pseudo-instructions: 
  - NOP (expands to ADDI x0, x0, 0)
  - LA rd, label (load address - expands to LUI + ADDI)
  - CALL label (call function - expands to JAL ra, label)
  - RET (return from function - expands to JALR zero, ra, 0)

### Labels
- Assembly code uses labels instead of absolute addresses
- Labels are automatically resolved during assembly
- Format: `label_name:` for definition, use label name in instructions

### CPU Clock
- Configurable execution speed (1 Hz to 10 kHz or unlimited)
- Command-line options: `--clock-hz`, `--no-clock`
- Used for realistic timing simulation

### Visualization
- Rich-based terminal UI for CPU state
- Live display mode with `-l` flag
- Step-by-step execution with `-s` flag

## Testing
- Use pytest for all tests
- Test structure:
  - `tests/unit/` - Unit tests for individual components
  - `tests/integration/` - Integration tests
  - `tests/programs/` - Assembly program tests
- Run with: `uv run pytest` or `./run_tests.sh`
- Coverage reports in `htmlcov/`

## Coding Conventions
- Python 3.13+ required
- Use type hints where appropriate
- Follow PEP 8 style guidelines
- Use `rich` library for terminal output and formatting
- Exception handling: Custom `VMError` class for VM-specific errors
- Logging: Use Python's `logging` module (configured in main.py)

## Common Commands
```bash
# Run a program
uv run python main.py examples/hello.asm

# Run with specific clock speed
uv run python main.py examples/counter.asm --clock-hz 100

# Run without clock (maximum speed)
uv run python main.py examples/counter.asm --no-clock

# Debug mode
uv run python main.py examples/test.asm -d

# Step-by-step with CPU visualization
uv run python main.py examples/test.asm -s -l

# Run tests
uv run pytest
./run_tests.sh

# Run specific test file
uv run pytest tests/unit/test_cpu.py
```

## Important Notes
- Register x0 is always zero (hardwired)
- Memory addresses must be word-aligned (4-byte boundaries)
- Stack grows downward from high memory
- Interrupts use special registers: mtvec (handler), mepc (return PC), mcause (cause)
- Timer interrupts are edge-triggered
- WFI instruction waits for interrupts (prevents busy-waiting)

## When Making Changes
- Always run tests after modifications: `./run_tests.sh`
- Update documentation in `docs/` if adding features
- Add example programs in `examples/` for new instructions
- Use `uv` for all Python operations
- Consider clock timing implications for new features
- Update CPU visualization if adding new CPU state