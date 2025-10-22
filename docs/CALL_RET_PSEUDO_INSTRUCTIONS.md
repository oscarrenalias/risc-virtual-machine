# CALL and RET Pseudo-Instructions

## Overview

The `CALL` and `RET` pseudo-instructions provide a convenient and readable way to implement function calls and returns in RISC-V assembly. They simplify the common pattern of saving the return address and jumping to/from functions.

## Syntax

### CALL

```asm
CALL label
```

Where:
- `label` - A label defined in the `.text` section representing a function

### RET

```asm
RET
```

No operands required - simply returns to the address stored in the `ra` (return address) register.

## How They Work

Both `CALL` and `RET` are **pseudo-instructions**, meaning they don't correspond to actual machine instructions. Instead, the assembler expands them into standard RISC-V instructions:

### CALL Expansion

```asm
CALL function_name
```

Expands to:

```asm
JAL ra, function_name    # Jump and link, save return address in ra (x1)
```

### RET Expansion

```asm
RET
```

Expands to:

```asm
JALR zero, ra, 0         # Jump to address in ra, discard return address
```

## Why Use CALL/RET?

### Improved Readability

**Before (using JAL/JALR):**
```asm
main:
    JAL ra, print_hello
    JAL ra, calculate
    JALR zero, ra, 0
```

**After (using CALL/RET):**
```asm
main:
    CALL print_hello
    CALL calculate
    RET
```

### RISC-V Standard Compliance

Standard RISC-V assemblers support these pseudo-instructions, making your code more portable and easier to understand for those familiar with RISC-V conventions.

### Clear Intent

- `CALL` clearly indicates "call this function"
- `RET` clearly indicates "return from this function"
- Compared to `JAL ra, ...` or `JALR zero, ra, 0` which require more mental parsing

## Examples

### Simple Function Call

```asm
.text
main:
    ADDI a0, zero, 42       # Prepare argument
    CALL square             # Call function
    # Result is in a0
    HALT

square:
    # Input: a0 = number
    # Output: a0 = number * number
    MUL a0, a0, a0          # a0 = a0 * a0
    RET                     # Return to caller
```

### Nested Function Calls

When calling functions from within functions, you need to save the `ra` register on the stack:

```asm
.text
main:
    ADDI a0, zero, 5
    CALL factorial
    # Result is in a0
    HALT

factorial:
    # Input: a0 = n
    # Output: a0 = n!
    
    # Base case: if n <= 1, return 1
    ADDI t0, zero, 1
    BLE a0, t0, factorial_base
    
    # Recursive case: save ra and n
    ADDI sp, sp, -8
    SW ra, 0(sp)            # Save return address
    SW a0, 4(sp)            # Save n
    
    # Call factorial(n-1)
    ADDI a0, a0, -1
    CALL factorial          # Recursive call
    
    # Restore n and multiply
    LW t0, 4(sp)            # Restore n
    MUL a0, a0, t0          # result = factorial(n-1) * n
    
    # Restore ra and return
    LW ra, 0(sp)
    ADDI sp, sp, 8
    RET

factorial_base:
    ADDI a0, zero, 1
    RET
```

### Multiple Function Calls

```asm
.text
main:
    CALL init_display
    CALL print_header
    CALL process_data
    CALL print_footer
    HALT

init_display:
    # Initialize display memory
    LUI a0, 0xF0
    ADDI a1, zero, 32       # Space character
    # ... clear screen ...
    RET

print_header:
    # Print header text
    LA a0, header_msg
    CALL print_string
    RET

process_data:
    # Process some data
    # ...
    RET

print_footer:
    # Print footer text
    LA a0, footer_msg
    CALL print_string
    RET

print_string:
    # Print null-terminated string
    # a0 = address of string
    # ...
    RET

.data
header_msg: .string "=== Program Start ==="
footer_msg: .string "=== Program End ==="
```

### Function with Multiple Arguments

```asm
.text
main:
    ADDI a0, zero, 10       # First argument
    ADDI a1, zero, 20       # Second argument
    ADDI a2, zero, 30       # Third argument
    CALL add_three
    # Result is in a0
    HALT

add_three:
    # Input: a0, a1, a2 = three numbers
    # Output: a0 = sum of three numbers
    ADD a0, a0, a1
    ADD a0, a0, a2
    RET
```

## Register Usage Conventions

When using `CALL` and `RET`, follow these RISC-V ABI conventions:

### Caller-Saved Registers (Must be saved by caller if needed)
- `a0-a7` - Function arguments and return values
- `t0-t6` - Temporary registers
- `ra` - Return address (automatically saved by CALL/JAL)

### Callee-Saved Registers (Must be preserved by function)
- `s0-s11` - Saved registers
- `sp` - Stack pointer

### Example of Proper Register Usage

```asm
compute_sum:
    # This function uses s0, so we must save it
    ADDI sp, sp, -4
    SW s0, 0(sp)            # Save s0 (callee-saved)
    
    # Use s0 for computation
    ADD s0, a0, a1
    ADDI s0, s0, 100
    
    # Put result in a0
    ADDI a0, s0, 0
    
    # Restore s0 before returning
    LW s0, 0(sp)
    ADDI sp, sp, 4
    RET
```

## Stack Management with CALL/RET

The stack is critical for managing nested function calls:

```asm
complex_function:
    # Prologue: allocate stack frame
    ADDI sp, sp, -16
    SW ra, 0(sp)            # Save return address
    SW s0, 4(sp)            # Save s0
    SW s1, 8(sp)            # Save s1
    SW s2, 12(sp)           # Save s2
    
    # Function body
    CALL helper1
    ADDI s0, a0, 0          # Save result
    
    CALL helper2
    ADDI s1, a0, 0          # Save result
    
    ADD a0, s0, s1          # Combine results
    
    # Epilogue: restore and return
    LW s2, 12(sp)           # Restore s2
    LW s1, 8(sp)            # Restore s1
    LW s0, 4(sp)            # Restore s0
    LW ra, 0(sp)            # Restore return address
    ADDI sp, sp, 16         # Deallocate stack frame
    RET
```

## Comparison with JAL/JALR

| Operation | Using CALL/RET | Using JAL/JALR |
|-----------|----------------|----------------|
| Call function | `CALL func` | `JAL ra, func` |
| Return | `RET` | `JALR zero, ra, 0` |
| Call and ignore return | N/A (use JAL) | `JAL zero, func` |
| Return to different address | N/A (use JALR) | `JALR zero, t0, 0` |

### When to Use Each

**Use CALL/RET when:**
- Following standard function call conventions
- You want maximum code readability
- Writing code that mimics standard RISC-V style

**Use JAL/JALR directly when:**
- You need non-standard behavior (e.g., tail calls)
- You want to save return address in a register other than `ra`
- You're implementing advanced control flow

## Tips and Best Practices

1. **Always pair CALL with RET**: Every function entered with `CALL` should exit with `RET`

2. **Save `ra` for nested calls**: If your function calls other functions, save `ra` on the stack:
   ```asm
   function:
       ADDI sp, sp, -4
       SW ra, 0(sp)
       CALL other_function
       LW ra, 0(sp)
       ADDI sp, sp, 4
       RET
   ```

3. **Follow ABI conventions**: Use `a0-a7` for arguments, `s0-s11` for preserved values

4. **Document your functions**: Comment what arguments go in which registers
   ```asm
   # print_number
   # Input:  a0 = number to print
   # Output: none
   # Uses:   t0-t2
   print_number:
       # ...
       RET
   ```

5. **Check stack alignment**: On some RISC-V implementations, the stack should be 16-byte aligned

## Common Mistakes to Avoid

### ❌ Forgetting to save `ra` in nested calls
```asm
function1:
    CALL function2      # Overwrites ra!
    RET                 # Returns to wrong address!
```

### ✅ Correct version
```asm
function1:
    ADDI sp, sp, -4
    SW ra, 0(sp)
    CALL function2
    LW ra, 0(sp)
    ADDI sp, sp, 4
    RET
```

### ❌ Not restoring callee-saved registers
```asm
function:
    ADDI s0, zero, 100  # Modifies s0
    RET                 # Should have saved/restored s0!
```

### ✅ Correct version
```asm
function:
    ADDI sp, sp, -4
    SW s0, 0(sp)
    ADDI s0, zero, 100
    # ... use s0 ...
    LW s0, 0(sp)
    ADDI sp, sp, 4
    RET
```

## See Also

- [Instruction Set Documentation](INSTRUCTION_SET.md) - Complete instruction reference
- [Register ABI Names](REGISTER_ABI_NAMES.md) - Register naming conventions
- [Label Support](LABEL_SUPPORT.md) - Using labels in assembly
