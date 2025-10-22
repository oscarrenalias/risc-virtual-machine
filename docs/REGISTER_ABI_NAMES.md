# RISC-V ABI Register Names

## Overview

The RISC-V Virtual Machine supports both **x-notation** (x0-x31) and **ABI (Application Binary Interface) names** for registers. ABI names make assembly code more readable by indicating the intended purpose of each register according to RISC-V calling conventions.

## Complete Register Mapping

| Register | ABI Name | Type | Description | Preserved Across Calls? |
|----------|----------|------|-------------|------------------------|
| x0 | zero | Constant | Hard-wired zero | N/A |
| x1 | ra | Link | Return address | No (caller-saved) |
| x2 | sp | Pointer | Stack pointer | Yes (callee-saved) |
| x3 | gp | Pointer | Global pointer | N/A |
| x4 | tp | Pointer | Thread pointer | N/A |
| x5-x7 | t0-t2 | Temporary | Temporary registers | No (caller-saved) |
| x8 | s0/fp | Saved/Pointer | Saved register / Frame pointer | Yes (callee-saved) |
| x9 | s1 | Saved | Saved register | Yes (callee-saved) |
| x10-x11 | a0-a1 | Argument/Return | Function arguments / Return values | No (caller-saved) |
| x12-x17 | a2-a7 | Argument | Function arguments | No (caller-saved) |
| x18-x27 | s2-s11 | Saved | Saved registers | Yes (callee-saved) |
| x28-x31 | t3-t6 | Temporary | Temporary registers | No (caller-saved) |

## Register Categories

### Special Purpose Registers

- **zero (x0)**: Always reads as 0, writes are ignored
- **ra (x1)**: Return address for function calls
- **sp (x2)**: Stack pointer, points to top of stack
- **gp (x3)**: Global pointer (typically for accessing global data)
- **tp (x4)**: Thread pointer (for thread-local storage)

### Temporary Registers (t0-t6)

Caller-saved registers used for temporary values that don't need to be preserved across function calls.

```assembly
ADDI t0, zero, 10       # Use t0 for temporary calculation
ADDI t1, t0, 5          # t1 = 15
MUL t2, t0, t1          # t2 = 10 * 15 = 150
```

### Saved Registers (s0-s11)

Callee-saved registers that must be preserved across function calls. If a function uses these registers, it must save and restore their values.

```assembly
# Function prologue - save s0 if we use it
ADDI sp, sp, -4
SW s0, 0(sp)

# Use s0 for computation
ADDI s0, zero, 100
# ... do work ...

# Function epilogue - restore s0
LW s0, 0(sp)
ADDI sp, sp, 4
```

**Note**: s0 can also be used as a frame pointer (fp).

### Argument/Return Registers (a0-a7)

Used for passing function arguments and returning values.

- **a0-a1**: Also used for return values
- **a2-a7**: Additional arguments (beyond a0 and a1)

```assembly
# Prepare function arguments
ADDI a0, zero, 42       # First argument
ADDI a1, zero, 10       # Second argument
JAL ra, my_function     # Call function

# After return, a0 contains the result
SW a0, 0(sp)            # Store result
```

## Usage Examples

### Using Both Notations

Both x-notation and ABI names can be used interchangeably, even in the same program:

```assembly
# These are equivalent
ADDI x10, x0, 42
ADDI a0, zero, 42

# Can mix notations
ADD a0, x10, t1         # a0 = x10 + t1 (x6)
```

### Hello World with ABI Names

```assembly
# Load display base address
LUI a0, 0xF0            # a0 = 0xF0000

# Write 'H'
ADDI a1, zero, 'H'
SW a1, 0(a0)

# Write 'i'
ADDI a1, zero, 'i'
SW a1, 4(a0)

HALT
```

### Function Call Example

```assembly
main:
    # Setup arguments
    ADDI a0, zero, 5        # First argument
    ADDI a1, zero, 3        # Second argument
    
    # Save return address area
    ADDI sp, sp, -4
    SW ra, 0(sp)
    
    # Call function
    JAL ra, multiply
    
    # Result is in a0
    # Restore and return
    LW ra, 0(sp)
    ADDI sp, sp, 4
    HALT

multiply:
    # Arguments in a0, a1
    # Result will be in a0
    MUL a0, a0, a1          # a0 = a0 * a1
    JALR zero, ra, 0        # Return
```

## Best Practices

### 1. Choose One Style Per File

While mixing is supported, prefer consistency within a single file:

```assembly
# Good: Consistent use of ABI names
ADDI a0, zero, 10
ADD a1, a0, t0
SW a1, 0(sp)

# Also good: Consistent use of x-notation
ADDI x10, x0, 10
ADD x11, x10, x5
SW x11, 0(x2)

# Less readable: Mixing without reason
ADDI a0, x0, 10         # Inconsistent
ADD x11, a0, t0         # Mixing styles
```

### 2. Use ABI Names for Readability

ABI names make code intent clearer:

```assembly
# Less clear
ADDI x10, x0, 42
ADDI x2, x2, -16
SW x10, 0(x2)

# More clear
ADDI a0, zero, 42       # Put 42 in return/argument register
ADDI sp, sp, -16        # Allocate stack space
SW a0, 0(sp)            # Store on stack
```

### 3. Follow Calling Conventions

When writing functions, respect the calling convention:

```assembly
my_function:
    # Save callee-saved registers you use
    ADDI sp, sp, -8
    SW s0, 0(sp)
    SW s1, 4(sp)
    
    # Use s0, s1 for computation
    ADDI s0, a0, 0          # Copy argument
    ADDI s1, a1, 0          # Copy argument
    
    # Do work...
    ADD a0, s0, s1          # Put result in a0
    
    # Restore callee-saved registers
    LW s0, 0(sp)
    LW s1, 4(sp)
    ADDI sp, sp, 8
    
    JALR zero, ra, 0        # Return
```

### 4. Document Register Usage

Add comments explaining register usage in complex code:

```assembly
# Register usage:
#   a0: input number
#   a1: divisor counter
#   t0: temporary for calculations
#   s0: saved result

check_prime:
    ADDI a1, zero, 2        # Start with divisor = 2
    # ...
```

## Display Format

When viewing CPU state, registers are displayed showing both notations:

```
x0/zero    : 0x00000000
x1/ra      : 0x00000000
x2/sp      : 0x000BFFFC
x5/t0      : 0x0000002A
x10/a0     : 0x00000064
```

This helps you:
- Understand the register's purpose (ABI name)
- Reference it precisely in code (x-notation or ABI name)
- Debug using either notation

## Case Insensitivity

Register names are case-insensitive:

```assembly
# All equivalent
ADDI a0, zero, 10
ADDI A0, ZERO, 10
ADDI a0, Zero, 10
```

## Reference Quick Guide

### Temporaries (don't preserve)
- `t0-t2` (x5-x7)
- `t3-t6` (x28-x31)

### Arguments/Returns (don't preserve)
- `a0-a7` (x10-x17)

### Saved (must preserve)
- `s0-s11` (x8-x9, x18-x27)

### Special (preserve sp, don't touch others)
- `zero` (x0) - constant 0
- `ra` (x1) - return address
- `sp` (x2) - stack pointer
- `gp` (x3) - global pointer
- `tp` (x4) - thread pointer

## See Also

- [Instruction Set Documentation](INSTRUCTION_SET.md)
- [RISC-V Calling Convention](https://riscv.org/wp-content/uploads/2015/01/riscv-calling.pdf)
- [CPU Visualization](CPU_VISUALIZATION.md)
