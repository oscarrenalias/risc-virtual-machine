# Enhanced Exception Reporting

The RISC VM includes comprehensive exception reporting to help with debugging and learning assembly programming.

## Features

When a CPU exception occurs, the VM now provides:

### 1. **Exception Classification**
- Type and category of the exception
- Human-readable error message
- Helpful hints for fixing the issue

### 2. **Instruction Context**
Shows the instruction that caused the exception plus 2 instructions before and after:
```
Instruction Context:
  [0x0020] SW x7, 0(x2)
  [0x0024] ADDI x8, x0, 0
→ [0x0028] SW x5, 0(x8)  ← EXCEPTION HERE
  [0x002C] HALT
```

### 3. **Complete Register State**
All 32 general-purpose registers with:
- Register number (x0-x31)
- ABI name (zero, ra, sp, etc.)
- Hexadecimal value
- Signed decimal value

Example:
```
Register State:
  x 0 (zero ): 0x00000000 (          0) | x 1 (ra   ): 0x00000020 (         32)
  x 2 (sp   ): 0x000BFFF0 (     786416) | x 3 (gp   ): 0x00000000 (          0)
  ...
```

### 4. **Control and Status Registers (CSRs)**
Shows all CSR values with interpretation:
```
Control and Status Registers (CSRs):
  MSTATUS  (0x300): 0x00000000
           └─ MIE (Machine Interrupt Enable): DISABLED
  MIE      (0x304): 0x00000000
           ├─ MTIE (Cycle Timer Int Enable): NO
           └─ RTIE (Real-time Timer Int Enable): NO
```

### 5. **Stack State**
Displays:
- Current stack pointer (SP)
- Stack usage (bytes used out of 256KB)
- Top 8 words of the stack with values
- Detection of stack overflow/underflow

Example:
```
Stack State (grows down from 0xBFFFC):
  SP: 0x000BFFF0 (16 bytes used of 256KB)

  Top 8 words:
  → [0x000BFFF0]: 0x0000012C (        300)
    [0x000BFFF4]: 0x000000C8 (        200)
    [0x000BFFF8]: 0x00000064 (        100)
    [0x000BFFFC]: 0x00000000 (          0)
```

### 6. **Interrupt and Timer State**
Shows:
- Global interrupt enable status
- WFI (wait-for-interrupt) state
- Pending interrupts
- Enabled interrupt sources
- Cycle-based timer state
- Real-time timer state

### 7. **Memory Region Analysis**
For memory access errors, identifies:
- Which memory region the address belongs to
- Valid address ranges
- Memory protection status
- Complete memory layout

Example:
```
Memory Region Analysis:
  Address: 0x00000000

  Region: TEXT SEGMENT (program code)
  Range: 0x00000 - 0x0FFFF (64KB)
  Protection: READ-ONLY
```

### 8. **Memory Hexdump**
For memory access errors, shows a hexdump of memory around the faulting address:
```
Memory dump around 0x10000000:
  [0x0FFFFFD0]: ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??  |????????????????|
→ [0x10000000]: ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??  |????????????????|
```

## Exception Types Detected

The system recognizes and provides specific help for:

- **MemoryAccessError**: Out of bounds or unaligned memory access
- **MemoryProtectionError**: Attempting to write to protected memory (e.g., text segment)
- **ValueError**: Invalid register or CSR address
- **VMError**: PC out of bounds, unknown instructions
- **Other exceptions**: General execution errors

## Example Output

Here's what you see when an exception occurs:

```
================================================================================
================================ CPU EXCEPTION =================================
================================================================================

Exception Type: MemoryAccessError
Category: Memory Access Violation
Message: Memory access out of bounds: 0x10000000 (size: 4)

Hints:
  • Address is outside valid memory range (0x00000 - 0xFFFFF)

--------------------------------------------------------------------------------

[Full register dump, stack state, and context as described above]

================================================================================
```

## Testing

Three test programs are provided to demonstrate the exception reporting:

1. **test_error_reporting.asm** - Out of bounds memory access
2. **test_alignment_error.asm** - Unaligned memory access
3. **test_stack_and_protection.asm** - Memory protection violation with stack usage

Run with:
```bash
uv run python main.py examples/test_error_reporting.asm
uv run python main.py examples/test_alignment_error.asm
uv run python main.py examples/test_stack_and_protection.asm -p  # -p enables protection
```

## For Developers

The exception reporting system is implemented in `src/debugger.py`:

- **CPUDebugger class**: Contains methods to format various aspects of CPU state
- **format_exception_report()**: Main function that generates comprehensive reports
- **Enhanced VMError**: Exception class that captures full VM state

The VM automatically uses this system when any exception occurs during program execution.
