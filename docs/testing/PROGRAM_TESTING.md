# Testing Complex Programs - Guide

This guide explains how to test complex, multi-feature programs in the RISC Virtual Machine.

## Why Test Complex Programs?

**Unit tests** verify individual components work correctly in isolation.  
**Integration tests** verify instructions execute correctly through the VM.  
**Program tests** verify that **real-world programs** combining multiple features work end-to-end.

Program tests catch issues that unit and integration tests miss:
- Unexpected interactions between features
- State management across multiple instructions
- Resource usage patterns (registers, memory, stack)
- Complex control flow edge cases
- Performance characteristics

## Testing Philosophy

### Start Simple, Build Complexity
```
1. Basic loops → 2. Nested loops → 3. Function calls → 4. Recursive algorithms
```

### Test Real Algorithms
Use actual algorithms people would write:
- **Factorial**: Loops, multiplication via addition
- **Fibonacci**: State management, multiple counters
- **Array operations**: Memory addressing, data processing
- **String operations**: Byte-level manipulation, null termination
- **Sorting algorithms**: Complex nested loops, comparisons
- **Search algorithms**: Early loop exits, conditional logic

### Verify Multiple Aspects
For each program, test:
- ✅ Correct output (result registers)
- ✅ No crashes/hangs (instruction count limits)
- ✅ Proper state cleanup (stack pointer, memory)
- ✅ Edge cases (empty input, boundary values)

## Program Test Patterns

### Pattern 1: Computational Algorithm

**Example: Factorial**

```python
def test_factorial_5(self, vm):
    """Test factorial calculation using repeated addition"""
    program = """
    # Input: x10 = n
    # Output: x11 = n!
    
    ADDI x10, x0, 5      # n = 5
    ADDI x11, x0, 1      # result = 1
    
loop:
    BEQ x10, x0, done    # if n == 0, done
    
    # Multiply result * n using repeated addition
    # (no MUL instruction available)
    ADDI x12, x11, 0     # temp = result
    ADDI x13, x10, -1    # counter = n - 1
    
mult_loop:
    BEQ x13, x0, mult_done
    ADD x11, x11, x12    # result += temp
    ADDI x13, x13, -1
    JAL x0, mult_loop
    
mult_done:
    ADDI x10, x10, -1    # n--
    JAL x0, loop
    
done:
    HALT
    """
    
    result = run_and_get_register(vm, program, 11)
    assert result == 120
    
    # Can also test edge cases
    # - factorial(0) = 1
    # - factorial(1) = 1
    # - factorial(10) = 3628800
```

**What it tests:**
- Loop termination
- Register reuse
- Nested loop control
- Arithmetic correctness

### Pattern 2: Data Structure Operations

**Example: Array Sum**

```python
def test_array_sum(self, vm):
    """Test summing array elements"""
    program = """
    # Initialize array in memory
    LUI x1, 0x2          # Array base = 0x2000
    
    # Store array: [1, 2, 3, 4, 5]
    ADDI x2, x0, 1
    SW x2, 0(x1)
    ADDI x2, x0, 2
    SW x2, 4(x1)
    ADDI x2, x0, 3
    SW x2, 8(x1)
    ADDI x2, x0, 4
    SW x2, 12(x1)
    ADDI x2, x0, 5
    SW x2, 16(x1)
    
    # Sum the array
    ADDI x10, x0, 5      # Count
    ADDI x11, x0, 0      # Sum accumulator
    ADDI x12, x0, 0      # Index (in bytes)
    
loop:
    BEQ x10, x0, done    # if count == 0, done
    ADD x13, x1, x12     # Address = base + index
    LW x14, 0(x13)       # Load element
    ADD x11, x11, x14    # Add to sum
    ADDI x12, x12, 4     # Next element (4 bytes)
    ADDI x10, x10, -1    # Decrement count
    JAL x0, loop
    
done:
    HALT
    """
    
    result = run_and_get_register(vm, program, 11)
    assert result == 15  # 1+2+3+4+5 = 15
```

**What it tests:**
- Memory initialization
- Pointer arithmetic
- Loop-based array traversal
- Accumulator pattern

### Pattern 3: Function Call with Stack

**Example: Nested Function Calls**

```python
def test_nested_function_calls(self, vm):
    """Test nested function calls with stack"""
    program = """
    # Setup stack pointer
    LUI x2, 0x10         # sp = 0x10000
    
    # Call outer function
    ADDI x10, x0, 3      # Argument = 3
    JAL x1, double_and_add
    
    HALT
    
double_and_add:
    # Save return address on stack
    ADDI x2, x2, -4
    SW x1, 0(x2)
    
    # Save argument
    ADDI x2, x2, -4
    SW x10, 0(x2)
    
    # Call inner function (double)
    JAL x1, double_it
    
    # Restore argument
    LW x10, 0(x2)
    ADDI x2, x2, 4
    
    # Add 5 to doubled value
    ADDI x11, x11, 5
    
    # Restore return address
    LW x1, 0(x2)
    ADDI x2, x2, 4
    
    JALR x0, x1, 0       # Return
    
double_it:
    # x10 = input, x11 = output
    ADD x11, x10, x10    # result = input * 2
    JALR x0, x1, 0       # Return
    """
    
    result = run_and_get_register(vm, program, 11)
    assert result == 11  # double(3) + 5 = 6 + 5 = 11
```

**What it tests:**
- Stack push/pop operations
- Return address preservation
- Argument passing
- Nested call handling
- Stack pointer management

### Pattern 4: Search/Filter Operations

**Example: Array Search with Early Exit**

```python
def test_array_search(self, vm):
    """Test searching for value in array"""
    program = """
    # Initialize array: [3, 5, 7, 9]
    LUI x1, 0x4
    ADDI x2, x0, 3
    SW x2, 0(x1)
    ADDI x2, x0, 5
    SW x2, 4(x1)
    ADDI x2, x0, 7
    SW x2, 8(x1)
    ADDI x2, x0, 9
    SW x2, 12(x1)
    
    ADDI x10, x0, 7      # Search value
    ADDI x11, x0, 4      # Count
    ADDI x12, x0, -1     # Result index (not found)
    ADDI x13, x0, 0      # Current index
    
loop:
    BEQ x11, x0, done    # if count == 0, done
    
    # Load current element
    SLLI x14, x13, 2     # Index * 4 (word size)
    ADD x14, x1, x14     # Calculate address
    LW x15, 0(x14)       # Load element
    
    # Check if found
    BEQ x15, x10, found  # if element == search_value
    
    # Continue searching
    ADDI x13, x13, 1     # index++
    ADDI x11, x11, -1    # count--
    JAL x0, loop
    
found:
    ADDI x12, x13, 0     # Save found index
    
done:
    HALT
    """
    
    result = run_and_get_register(vm, program, 12)
    assert result == 2   # Found at index 2
```

**What it tests:**
- Early loop termination
- Shift instruction (SLLI)
- Conditional branching
- Result initialization (not found case)

## Common Challenges

### Challenge 1: No Multiply Instruction

**Solution**: Use repeated addition in a loop
```assembly
# Multiply x10 * x11 → x12
ADDI x12, x0, 0      # result = 0
mult_loop:
    BEQ x11, x0, done
    ADD x12, x12, x10  # result += x10
    ADDI x11, x11, -1  # x11--
    JAL x0, mult_loop
done:
```

### Challenge 2: No BLE/BGT Instructions

**Solution**: Use combinations of available branches
```assembly
# Instead of: BLE x1, x2, target
# Use: 
BLT x2, x1, skip     # if x2 < x1, skip the jump
JAL x0, target       # else, jump to target
skip:

# Or combine with BEQ:
BEQ x1, x2, target   # if x1 == x2, jump
BLT x1, x2, target   # if x1 < x2, jump
# Falls through if x1 > x2
```

### Challenge 3: Limited Immediate Values

**Solution**: Use LUI + ADDI for large values
```assembly
# To load 0x12345678:
LUI x1, 0x12345      # Load upper 20 bits
ADDI x1, x1, 0x678   # Add lower 12 bits
```

### Challenge 4: Word Alignment Requirements

**Solution**: Ensure memory addresses are 4-byte aligned
```assembly
LUI x1, 0x2          # 0x2000 (aligned)
SW x2, 0(x1)         # OK
SW x2, 4(x1)         # OK (0x2004)
# SW x2, 2(x1)       # ERROR: not aligned!
```

## Testing Best Practices

### 1. Test Edge Cases
```python
# Factorial tests
test_factorial_0()   # Base case
test_factorial_1()   # Minimal case
test_factorial_5()   # Normal case
test_factorial_10()  # Larger value
```

### 2. Set Instruction Limits
```python
# Prevent infinite loops
run_program_until_halt(vm, program, max_instructions=1000)
```

### 3. Check Multiple Registers
```python
# Verify state
result = vm.cpu.read_register(10)
counter = vm.cpu.read_register(11)
status = vm.cpu.read_register(12)
assert result == expected
assert counter == 0  # Verify counter decremented to 0
```

### 4. Test Memory State
```python
# Check array was modified
assert vm.memory.read_word(0x2000) == expected_value
assert vm.memory.display.buffer[0][0] == 'A'
```

### 5. Use Descriptive Test Names
```python
# Good
def test_factorial_returns_one_for_zero_input(self, vm):

# Better than
def test_factorial_1(self, vm):
```

## Real-World Example: Bubble Sort

```python
def test_bubble_sort(self, vm):
    """Test bubble sort algorithm"""
    program = """
    # Array to sort: [5, 2, 8, 1, 9]
    LUI x1, 0x2          # Array base
    
    # Initialize array
    ADDI x2, x0, 5
    SW x2, 0(x1)
    ADDI x2, x0, 2
    SW x2, 4(x1)
    ADDI x2, x0, 8
    SW x2, 8(x1)
    ADDI x2, x0, 1
    SW x2, 12(x1)
    ADDI x2, x0, 9
    SW x2, 16(x1)
    
    ADDI x10, x0, 5      # Array length
    
outer_loop:
    BEQ x10, x0, done    # if length == 0, done
    ADDI x11, x0, 0      # Inner index = 0
    ADDI x12, x10, -1    # Inner limit = length - 1
    
inner_loop:
    BGE x11, x12, outer_next  # if index >= limit, next outer
    
    # Load adjacent elements
    SLLI x13, x11, 2     # offset = index * 4
    ADD x14, x1, x13     # addr1 = base + offset
    LW x15, 0(x14)       # element1
    LW x16, 4(x14)       # element2
    
    # Compare and swap if needed
    BGE x16, x15, no_swap  # if elem2 >= elem1, no swap
    
    # Swap
    SW x16, 0(x14)
    SW x15, 4(x14)
    
no_swap:
    ADDI x11, x11, 1     # index++
    JAL x0, inner_loop
    
outer_next:
    ADDI x10, x10, -1    # length--
    JAL x0, outer_loop
    
done:
    # Verify sorted: load first element
    LW x20, 0(x1)
    HALT
    """
    
    run_program_until_halt(vm, program, max_instructions=10000)
    
    # Check array is sorted
    assert vm.memory.read_word(0x2000) == 1  # [1, 2, 5, 8, 9]
    assert vm.memory.read_word(0x2004) == 2
    assert vm.memory.read_word(0x2008) == 5
    assert vm.memory.read_word(0x200C) == 8
    assert vm.memory.read_word(0x2010) == 9
```

**What this tests:**
- Nested loops with different bounds
- Array element comparison
- Conditional swapping
- Complex memory operations
- Algorithm correctness

## Debugging Program Tests

### 1. Add Debug Output
```python
vm_debug = create_vm(debug=True)
vm_debug.load_program(program)
# Will print instruction execution
```

### 2. Check Register State
```python
# After test failure, inspect:
for i in range(1, 32):
    print(f"x{i} = {vm.cpu.read_register(i)}")
```

### 3. Verify Memory
```python
# Check specific addresses
for addr in range(0x2000, 0x2020, 4):
    val = vm.memory.read_word(addr)
    print(f"0x{addr:08X}: {val}")
```

### 4. Count Instructions
```python
count = run_program_until_halt(vm, program, max_instructions=1000)
print(f"Executed {count} instructions")
# If count == 1000, likely infinite loop
```

## Next Steps

1. **Expand test coverage**: Add more complex programs
2. **Test edge cases**: Boundary conditions, error cases
3. **Performance tests**: Verify instruction counts for algorithms
4. **Real examples**: Port `examples/*.asm` to test suite
5. **Stress tests**: Large arrays, deep recursion, complex control flow

## See Also

- [Integration Testing Guide](INTEGRATION_TESTING.md) - Layer 2 tests
- [Unit Testing Guide](tests/README.md) - Layer 1 tests
- [Testing Summary](../TESTING.md) - Quick reference
