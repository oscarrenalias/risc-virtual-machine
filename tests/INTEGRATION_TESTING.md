# Integration and Program Testing

This document explains Layers 2 & 3 of the testing pyramid: **Integration Tests** and **Program Tests**.

## Overview

After establishing a solid foundation with unit tests (Layer 1), we now test:
- **Integration Tests (Layer 2)**: Individual instructions executing through the full VM stack
- **Program Tests (Layer 3)**: Complete programs that test multiple features together

## Test Structure

```
tests/
├── unit/               # Layer 1: Component-level tests (154 tests)
├── integration/        # Layer 2: Instruction & component interaction (30 tests)
│   ├── test_instructions.py      # Individual instruction execution
│   └── test_interrupts.py        # Interrupt & timer integration
└── programs/           # Layer 3: Complete program tests (15 tests)
    └── test_programs.py          # Full programs (factorial, fibonacci, etc.)
```

## Integration Tests (Layer 2)

### test_instructions.py

Tests individual instructions executing through the complete VM (assembler → CPU → memory).

**Test Classes:**
- **TestArithmeticInstructions** (4 tests)
  - Basic arithmetic (ADD, SUB)
  - Overflow wrapping behavior
  - Negative results

- **TestLogicalInstructions** (3 tests)
  - AND, OR, XOR operations
  - Bitwise logic verification

- **TestShiftInstructions** (3 tests)
  - SLL (shift left logical)
  - SRL (shift right logical)
  - SRA (shift right arithmetic with sign extension)

- **TestComparisonInstructions** (2 tests)
  - SLT (set less than, signed)
  - SLTU (set less than, unsigned)

- **TestMemoryInstructions** (3 tests)
  - Store and load word operations
  - Offset addressing
  - Byte operations (SB, LBU)

- **TestBranchInstructions** (4 tests)
  - BEQ taken/not taken
  - BNE branching
  - BLT comparisons

- **TestJumpInstructions** (2 tests)
  - JAL with return address saving
  - JALR indirect jumps

- **TestLUIInstruction** (2 tests)
  - Basic LUI operation
  - LUI + ADDI for full 32-bit values

- **TestLoopConstruct** (2 tests)
  - Simple counting loops
  - Accumulator loops

**Example:**
```python
def test_add_overflow(self, vm):
    """Test ADD with overflow wraps to 32-bit"""
    program = """
    LUI x1, 0xFFFFF      # x1 = 0xFFFFF000
    ADDI x1, x1, 0x7FF   # Construct 0xFFFFFFFF
    ADDI x1, x1, 0x7FF   
    ADDI x1, x1, 1       
    ADDI x2, x0, 2
    ADD x3, x1, x2       # Should wrap around
    HALT
    """
    result = run_and_get_register(vm, program, 3)
    assert result == 1  # Wraps to 1
```

### test_interrupts.py

Tests interrupt handling, timers, WFI, and CSR operations through full VM execution.

**Test Classes:**
- **TestTimerInterrupts** (1 test)
  - Timer interrupt generation
  - Interrupt handler execution
  - Interrupt clearing

- **TestWFIWithInterrupts** (1 test)
  - WFI instruction behavior
  - Waking from WFI on timer interrupt

- **TestCSROperations** (3 tests)
  - CSRRW (read/write)
  - CSRRS (set bits)
  - CSRRC (clear bits)

- **TestInterruptPriority** (1 test, marked slow)
  - Multiple interrupt sources
  - Interrupt priority handling

**Example:**
```python
def test_basic_timer_interrupt(self, vm):
    """Test timer fires interrupt and handler executes"""
    # Sets up timer, enables interrupts, waits for interrupt
    # Verifies handler increments counter
    interrupt_count = vm.cpu.read_register(10)
    assert interrupt_count >= 1
```

## Program Tests (Layer 3)

### test_programs.py

Tests complete, realistic programs that exercise multiple VM features together.

**Test Classes:**
- **TestFactorialProgram** (3 tests)
  - Factorial of 5 (= 120)
  - Factorial of 0 (= 1)
  - Factorial of 10 (= 3,628,800)
  - Uses repeated addition for multiplication (no MUL instruction)
  - Tests: loops, conditionals, arithmetic

- **TestFibonacciProgram** (2 tests)
  - 10th Fibonacci number (= 55)
  - First 10 Fibonacci numbers (sequence validation)
  - Tests: loops, multiple registers, state management

- **TestStackOperations** (2 tests)
  - Simple function call with return
  - Nested function calls with stack
  - Tests: JAL/JALR, stack pointer, memory operations

- **TestArrayOperations** (2 tests)
  - Array sum calculation
  - Finding maximum element
  - Tests: memory addressing, loops, comparisons

- **TestComplexLoops** (2 tests)
  - Nested loops (multiplication via addition)
  - Loop with early exit (array search)
  - Tests: complex control flow, SLLI instruction

- **TestDisplayIntegration** (2 tests, marked slow)
  - Writing to display buffer
  - Display MMIO operations
  - Tests: memory-mapped I/O, word writes

- **TestRealWorldProgram** (1 test)
  - String length calculation
  - Null-terminated string handling
  - Tests: byte operations, loops, conditions

**Example:**
```python
def test_factorial_5(self, vm):
    """Test factorial of 5 (should be 120)"""
    # Complete factorial program using repeated addition
    # for multiplication (since no MUL instruction)
    result = run_and_get_register(vm, program, 11)
    assert result == 120
```

## Key Testing Patterns

### 1. Full VM Execution
All integration and program tests execute through the complete VM stack:
```python
vm.load_program(program_source)
count = 0
while not vm.cpu.halted and count < max_instructions:
    vm.step()
    count += 1
result = vm.cpu.read_register(reg_num)
```

### 2. Realistic Instruction Sequences
Programs use only supported instructions:
- **No MUL** - Use repeated addition
- **No BLE** - Use BEQ/BLT/BGE combinations
- **Word-aligned addresses** for most MMIO operations

### 3. Complex Control Flow
Tests verify:
- Branch taken/not taken paths
- Jump and link return addresses
- Nested loops with multiple counters
- Early loop exits (search patterns)

### 4. Memory Operations
Tests cover:
- Word and byte loads/stores
- Offset addressing
- Array access patterns
- Memory-mapped I/O

### 5. Interrupt Handling
Integration tests verify:
- Timer configuration
- Interrupt enable/disable
- Handler invocation
- MRET return from interrupt
- CSR operations (mtvec, mstatus, mie, mcause)

## Test Limitations

### Current Scope
- ✅ All arithmetic, logical, shift instructions
- ✅ Memory operations (load/store word/byte)
- ✅ All branch and jump instructions
- ✅ Timer interrupts (cycle-based)
- ✅ CSR operations
- ✅ Complex programs (factorial, fibonacci, arrays)

### Not Currently Tested
- ❌ RT timer interrupts in integration tests (slow)
- ❌ Byte writes to unaligned MMIO control registers
- ❌ Display cursor advancement (writes to buffer don't auto-advance cursor)
- ❌ Complex nested interrupt scenarios
- ❌ Stack overflow/underflow
- ❌ Memory protection faults

## Running Integration & Program Tests

```bash
# Run all integration tests
./run_tests.sh --test tests/integration/

# Run all program tests
./run_tests.sh --test tests/programs/

# Run specific test file
./run_tests.sh --test tests/integration/test_instructions.py

# Run with verbose output
./run_tests.sh --test tests/integration/ -v

# Run all tests (unit + integration + program)
./run_tests.sh

# With coverage
./run_tests.sh --coverage
```

## Coverage Impact

Adding integration and program tests increased coverage significantly:

| Module | Unit Tests Only | With Integration/Program | Improvement |
|--------|----------------|-------------------------|-------------|
| **Overall** | 55% | **70%** | **+15%** |
| vm.py | 45% | **62%** | **+17%** |
| assembler.py | 73% | **82%** | **+9%** |
| instruction.py | 55% | **62%** | **+7%** |

## Test Statistics

- **Total Tests**: 199 (up from 154)
- **Integration Tests**: 30
- **Program Tests**: 15
- **Execution Time**: ~0.33 seconds (fast feedback)
- **Pass Rate**: 100%

## Adding New Program Tests

### Pattern for Factorial-like Programs:
```python
def test_my_algorithm(self, vm):
    """Description of what algorithm computes"""
    program = """
    # Setup inputs
    ADDI x10, x0, input_value
    
    # Algorithm implementation
    # ... instructions ...
    
    HALT
    """
    result = run_and_get_register(vm, program, result_register)
    assert result == expected_value
```

### Pattern for Array Operations:
```python
def test_array_operation(self, vm):
    """Description of array operation"""
    program = """
    # Initialize array in memory
    LUI x1, base_address
    # ... store array elements ...
    
    # Process array
    # ... loop through elements ...
    
    HALT
    """
    result = run_and_get_register(vm, program, result_register)
    assert result == expected
```

### Pattern for Interrupt Tests:
```python
def test_interrupt_scenario(self, vm):
    """Description of interrupt scenario"""
    program = """
    # Setup handler
    ADDI x1, x0, handler
    CSRRW x0, 0x305, x1
    
    # Configure interrupt source
    # ... timer/device setup ...
    
    # Enable interrupts
    # ... mie, mstatus ...
    
    # Main loop
    # ... wait for interrupt ...
    
    HALT
    
handler:
    # Handle interrupt
    # ... do work ...
    MRET
    """
    run_program_until_halt(vm, program, max_instructions=1000)
    assert vm.cpu.read_register(counter_reg) > 0
```

## Best Practices

1. **Test One Concept**: Each test should verify one specific behavior
2. **Use Descriptive Names**: Test names should clearly state what is being tested
3. **Include Comments**: Assembly code in tests should have clear comments
4. **Set Reasonable Limits**: Use `max_instructions` to prevent infinite loops
5. **Verify State**: Check multiple registers/memory locations when relevant
6. **Mark Slow Tests**: Use `@pytest.mark.slow` for tests > 0.1s

## Future Enhancements

### Additional Program Tests
- Bubble sort algorithm
- Binary search
- String manipulation (copy, compare)
- Linked list operations
- Recursive functions

### Additional Integration Tests
- All branch instruction combinations (BLTU, BGEU)
- Halfword operations (LH, LHU, SH)
- AUIPC instruction
- CSR immediate variants (CSRRWI, CSRRSI, CSRRCI)
- Complex interrupt nesting scenarios

### Real Example Programs
- Port existing examples to test suite:
  - `examples/clock.asm` (with timer and display)
  - `examples/counter.asm` (with display updates)
  - `examples/pattern.asm` (display patterns)

## Troubleshooting

### Test Timeout
If tests hang, check:
- Loop termination conditions
- Branch instruction correctness
- WFI without enabled interrupts

### Wrong Results
If calculations are incorrect:
- Verify instruction operand order
- Check signed vs unsigned operations
- Confirm register usage (no conflicts)

### Assembly Errors
If program won't assemble:
- Check instruction syntax (e.g., `LUI x1, 0x1000` not `LUI x1, x0, 0x1000`)
- Verify label definitions match usage
- Ensure addresses are correctly formed

## See Also

- [Unit Testing Documentation](tests/README.md) - Layer 1 tests
- [Overall Testing Summary](../TESTING.md) - Quick reference
- [Test Runner Script](../run_tests.sh) - Running tests
