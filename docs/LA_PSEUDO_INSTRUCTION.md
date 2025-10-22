# LA (Load Address) Pseudo-Instruction

## Overview

The `LA` (Load Address) pseudo-instruction is a convenient way to load the full 32-bit address of a label into a register. It simplifies the common pattern of loading addresses for data structures, strings, and function pointers.

## Syntax

```asm
LA rd, label
```

Where:
- `rd` - Destination register (can use x-notation or ABI names)
- `label` - A label defined in either `.data` or `.text` section

## How It Works

`LA` is a **pseudo-instruction**, meaning it doesn't correspond to a single machine instruction. Instead, the assembler expands it into two instructions:

```asm
LA rd, label
```

Expands to:

```asm
LUI rd, %hi(label)      # Load upper 20 bits
ADDI rd, rd, %lo(label) # Add lower 12 bits
```

This allows loading the full 32-bit address, which wouldn't fit in a single immediate value.

## Examples

### Loading Data Addresses

```asm
.data
message: .string "Hello, World!"
counter: .word 42

.text
main:
    LA a0, message      # Load address of message into a0
    LA t0, counter      # Load address of counter into t0
    LW t1, 0(t0)        # Load the value (42) from counter
    HALT
```

### Loading Function Addresses (Function Pointers)

```asm
.text
main:
    LA t0, my_function  # Load address of function
    JALR ra, t0, 0      # Call function via register
    HALT

my_function:
    ADDI a0, a0, 10
    JALR zero, ra, 0
```

### Using with ABI Register Names

```asm
.data
array: .word 10, 20, 30, 40, 50

.text
    LA a0, array        # a0 = base address of array
    ADDI a1, a0, 4      # a1 = address of second element
    ADDI a2, a0, 8      # a2 = address of third element
    
    LW t0, 0(a0)        # t0 = 10
    LW t1, 0(a1)        # t1 = 20
    LW t2, 0(a2)        # t2 = 30
    HALT
```

## Comparison: Before and After LA

### Without LA (Manual Address Loading)

```asm
.data
str: .string "Test"

.text
    # Manually calculate and split the address
    LUI x10, 0x10       # Upper 20 bits of 0x10000
    ADDI x10, x10, 0    # Lower 12 bits
    # x10 now contains 0x10000
```

**Problems:**
- Error-prone: Must manually calculate address offsets
- Hard to maintain: If data layout changes, all addresses must be recalculated
- Not portable: Addresses are hardcoded

### With LA (Automatic Address Loading)

```asm
.data
str: .string "Test"

.text
    LA a0, str          # Clean and automatic!
    # a0 now contains address of str
```

**Benefits:**
- ✅ No manual address calculation
- ✅ Automatically updated if data layout changes
- ✅ More readable and maintainable
- ✅ Works with both data and text labels

## Address Resolution

The assembler resolves addresses during assembly:

1. **First Pass**: Records the address of each label
2. **LA Expansion**: Converts `LA` to `LUI` + `ADDI`
3. **Second Pass**: Calculates upper and lower bits
   - Upper 20 bits: `address >> 12`
   - Lower 12 bits: `address & 0xFFF`

### Example Resolution

```asm
.data
msg: .string "Hi"    # Located at 0x10000

.text
LA a0, msg
```

Expands to:

```asm
LUI a0, 0x10        # 0x10000 >> 12 = 0x10
ADDI a0, a0, 0      # 0x10000 & 0xFFF = 0x0
# Result: a0 = (0x10 << 12) | 0x0 = 0x10000
```

## Common Use Cases

### 1. String Processing

```asm
.data
hello: .string "Hello, World!"

.text
    LA a0, hello
    JAL ra, print_string
    HALT

print_string:
    # a0 contains string address
    # ... implementation ...
    JALR zero, ra, 0
```

### 2. Array Access

```asm
.data
numbers: .word 5, 10, 15, 20, 25

.text
    LA t0, numbers      # Base address
    LW a0, 0(t0)        # numbers[0]
    LW a1, 4(t0)        # numbers[1]
    LW a2, 8(t0)        # numbers[2]
    HALT
```

### 3. Jump Tables / Function Pointers

```asm
.text
main:
    LA t0, handler1
    LA t1, handler2
    
    # Call handler1
    JALR ra, t0, 0
    
    # Call handler2
    JALR ra, t1, 0
    HALT

handler1:
    ADDI a0, zero, 1
    JALR zero, ra, 0

handler2:
    ADDI a0, zero, 2
    JALR zero, ra, 0
```

### 4. Passing Data Structure Addresses

```asm
.data
config: .word 100, 200, 300, 400

.text
    LA a0, config       # Pass struct address as argument
    JAL ra, process_config
    HALT

process_config:
    LW t0, 0(a0)        # Access struct members
    LW t1, 4(a0)
    # ...
    JALR zero, ra, 0
```

## Register Compatibility

LA works with both x-notation and ABI register names:

```asm
# Both are valid:
LA x10, data        # Using x-notation
LA a0, data         # Using ABI name (same register)

# All register types work:
LA zero, data       # x0 (though pointless since x0 is hardwired to 0)
LA ra, data         # x1 - return address
LA sp, data         # x2 - stack pointer
LA t0, data         # x5 - temporary register
LA s0, data         # x8 - saved register
LA a0, data         # x10 - argument register
```

## Important Notes

1. **LA is case-insensitive**: `LA`, `La`, and `la` all work
2. **Two instructions**: Remember that LA expands to 2 instructions, affecting:
   - Program counter calculations
   - Jump/branch offset calculations
   - Memory usage (8 bytes instead of 4)
3. **Label must exist**: Using an undefined label will cause an assembly error
4. **Works with any label**: Both `.data` and `.text` labels are supported

## Performance Considerations

Since LA expands to two instructions:
- Takes 2 instruction cycles to execute
- Uses 8 bytes of program memory

For frequently used addresses in loops, consider loading once and reusing:

```asm
# Good: Load once outside loop
LA t0, array
ADDI t1, zero, 0

loop:
    ADD t2, t0, t1      # Use preloaded address
    LW a0, 0(t2)
    # ... process ...
    ADDI t1, t1, 4
    BLT t1, t2, loop

# Avoid: Loading inside loop
loop:
    LA t0, array        # Wasteful: 2 instructions every iteration
    # ...
```

## Error Handling

Common errors and solutions:

### Undefined Label
```asm
LA a0, undefined_label  # ERROR: Undefined label: undefined_label
```
**Solution**: Define the label in `.data` or `.text` section

### Wrong Number of Operands
```asm
LA a0                   # ERROR: LA instruction requires 2 operands
```
**Solution**: Provide both register and label: `LA a0, label`

### Invalid Register
```asm
LA x33, data            # ERROR: Invalid register: x33
```
**Solution**: Use valid register (x0-x31 or ABI names)

## See Also

- [Label Support Documentation](LABEL_SUPPORT.md)
- [Register ABI Names](REGISTER_ABI_NAMES.md)
- [Instruction Set](INSTRUCTION_SET.md)
