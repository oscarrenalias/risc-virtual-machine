# Label Support in Instructions

## Overview

The assembler now supports using labels directly in instructions instead of manually calculating memory addresses. This makes assembly code much more maintainable and less error-prone.

## How to use?

This is how it can be used:

```asm
# NEW WAY - Automatic! ✅
main:
    LUI x1, 0x0
    ADDI x1, x1, timer_handler    # Label automatically resolved!
    CSRRW x0, 0x305, x1

# ... many lines of code ...

timer_handler:              # Assembler calculates address automatically
    ADDI x3, x3, 1
    MRET
```

## Supported Instructions

Labels can now be used in the following instruction types:

### I-Type Instructions
- `ADDI`, `ANDI`, `ORI`, `XORI`
- `SLTI`, `SLTIU`
- `SLLI`, `SRLI`, `SRAI`

Example:
```asm
ADDI x1, x0, my_function    # x1 = address of my_function
ORI x2, x0, data_label      # x2 = address of data_label
```

### Branch Instructions
- `BEQ`, `BNE`, `BLT`, `BGE`, `BLTU`, `BGEU`

Example:
```asm
loop:
    ADDI x1, x1, 1
    BLT x1, x2, loop        # Branch back to loop
```

### Jump Instructions
- `JAL`

Example:
```asm
JAL x1, subroutine          # Jump to subroutine, save return address
```

## How It Works

The assembler performs a two-pass assembly:

1. **First Pass**: Scans the code and records the address of each label
2. **Second Pass**: Replaces label references with actual addresses

### Address Resolution

- **I-Type instructions**: Label is replaced with the absolute address
  ```asm
  ADDI x1, x0, handler    # Becomes: ADDI x1, x0, 124 (if handler is at byte 124)
  ```

- **Branch instructions**: Label is replaced with a relative offset from the current instruction
  ```asm
  BEQ x1, x2, target      # Becomes: BEQ x1, x2, 16 (if target is 16 bytes ahead)
  ```

- **Jump instructions**: Label is replaced with a relative offset from the current instruction
  ```asm
  JAL x1, function        # Becomes: JAL x1, 32 (if function is 32 bytes ahead)
  ```

## Common Use Cases

### 1. Setting Interrupt Handlers

**Before:**
```asm
LUI x1, 0x0
ADDI x1, x1, 380        # Must manually calculate handler address
CSRRW x0, 0x305, x1
```

**After:**
```asm
LUI x1, 0x0
ADDI x1, x1, timer_handler    # Automatic!
CSRRW x0, 0x305, x1
```

### 2. Building Jump Tables

**Before:**
```asm
ADDI x10, x0, 100       # case_0 address - must calculate manually
ADDI x11, x0, 116       # case_1 address
ADDI x12, x0, 132       # case_2 address
```

**After:**
```asm
ADDI x10, x0, case_0    # Assembler figures it out
ADDI x11, x0, case_1
ADDI x12, x0, case_2
```

### 3. Function Pointers

**Before:**
```asm
ADDI x5, x0, 256        # Pointer to callback function
SW x5, 0(x1)            # Store it
```

**After:**
```asm
ADDI x5, x0, callback   # Much clearer intent
SW x5, 0(x1)
```

## Examples

See the following example files:
- `examples/clock_with_labels.asm` - Digital clock using label-based addressing
- `test_label_support.py` - Comprehensive test suite

## Benefits

✅ **Maintainable**: Add/remove code without recalculating addresses  
✅ **Readable**: Labels are self-documenting  
✅ **Less error-prone**: No manual address arithmetic  
✅ **Refactoring-friendly**: Move code around freely  

## Error Handling

The assembler will report an error if you reference a label that doesn't exist:

```asm
ADDI x1, x0, undefined_label    # Error: Undefined label: undefined_label
```

## Technical Details

### Implementation

The changes were made in `src/assembler.py`:

1. Modified `_parse_instruction()` to accept labels in I-type immediate fields
2. Extended `_second_pass()` to resolve I-type label references to absolute addresses