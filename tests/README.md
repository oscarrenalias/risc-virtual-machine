# RISC Virtual Machine - Test Suite

## Overview

This directory contains the comprehensive test suite for the RISC Virtual Machine. The tests are organized following the **test pyramid** pattern with unit tests as the foundation.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # pytest configuration and fixtures
├── fixtures/
│   ├── __init__.py
│   └── test_helpers.py        # Helper functions and utilities
└── unit/                       # Unit tests for core components
    ├── test_cpu.py            # CPU tests (57 tests)
    ├── test_memory.py          # Memory tests (44 tests)
    ├── test_assembler.py       # Assembler tests (18 tests)
    ├── test_timer.py           # Timer tests (17 tests)
    ├── test_realtime_timer.py  # RT Timer tests (9 tests)
    └── test_display.py         # Display tests (9 tests)
```

## Test Coverage

**Total: 154 tests, 55% code coverage**

### Unit Test Coverage by Module

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| **CPU** | 57 | 97% | ✅ Excellent |
| **Timer** | 17 | 100% | ✅ Complete |
| **Memory** | 44 | 84% | ✅ Very Good |
| **RealTimeTimer** | 9 | 83% | ✅ Very Good |
| **Assembler** | 18 | 73% | ⚠️ Good |
| **Display** | 9 | 50% | ⚠️ Moderate |

## Running Tests

### Run All Tests
```bash
uv run pytest tests/unit/ -v
```

### Run Specific Test File
```bash
uv run pytest tests/unit/test_cpu.py -v
```

### Run Tests with Coverage
```bash
uv run pytest tests/unit/ --cov=src --cov-report=term-missing
```

### Run Tests with HTML Coverage Report
```bash
uv run pytest tests/unit/ --cov=src --cov-report=html
# Open htmlcov/index.html in your browser
```

### Run Only Fast Tests (Skip Slow Tests)
```bash
uv run pytest tests/unit/ -m "not slow"
```

## Test Categories

### 1. CPU Tests (`test_cpu.py`)
Tests CPU core functionality including:
- Register operations (read/write, x0 hardwired to zero)
- Program counter management
- CSR (Control and Status Register) operations
- Interrupt handling and priority
- WFI (Wait For Interrupt) functionality
- Sign extension utilities
- Interrupt state machine

**Classes:**
- `TestCPUBasics` - Initialization and basic state
- `TestRegisterOperations` - Register read/write/aliases
- `TestProgramCounter` - PC increment/set operations
- `TestCPUState` - Halt and reset functionality
- `TestSignExtension` - Sign extension and type conversion
- `TestCSROperations` - CSR read/write/atomic operations
- `TestInterruptControl` - Interrupt enable/disable
- `TestInterruptDetection` - Interrupt pending detection
- `TestInterruptHandling` - Interrupt entry/return (MRET)
- `TestWaitForInterrupt` - WFI state management

### 2. Memory Tests (`test_memory.py`)
Tests memory system including:
- Byte and word read/write operations
- Memory alignment enforcement
- Bounds checking
- Memory protection (text segment)
- Memory-mapped I/O (Display, Timer, RT Timer)
- Program loading
- Memory regions (text, data, heap, stack, MMIO)

**Classes:**
- `TestMemoryBasics` - Initialization and regions
- `TestByteOperations` - Byte-level access
- `TestWordOperations` - Word-level access with alignment
- `TestMemoryProtection` - Text segment protection
- `TestProgramLoading` - Program loading functionality
- `TestMemoryDump` - Memory dump utility
- `TestDisplayMemoryMapped` - Display MMIO
- `TestTimerMemoryMapped` - Timer MMIO
- `TestRTTimerMemoryMapped` - RT Timer MMIO
- `TestMemoryRegions` - Region accessibility

### 3. Assembler Tests (`test_assembler.py`)
Tests assembly parsing and code generation:
- R-type, I-type, S-type, B-type, J-type, U-type instructions
- Label definition and resolution
- Forward/backward references
- Comment handling
- Error detection and reporting

**Classes:**
- `TestAssemblerBasics` - Initialization
- `TestInstructionParsing` - All instruction types
- `TestLabelSupport` - Label definition/resolution
- `TestComments` - Comment parsing
- `TestErrorHandling` - Error detection
- `TestMultipleInstructions` - Complete programs

### 4. Timer Tests (`test_timer.py`)
Tests cycle-based timer functionality:
- Counter increment and compare matching
- Prescaler clock division
- One-shot and periodic modes
- Auto-reload functionality
- Interrupt generation
- Register access (counter, compare, control, prescaler)

**Classes:**
- `TestTimerBasics` - Initialization and reset
- `TestTimerTick` - Tick behavior and prescaler
- `TestTimerModes` - One-shot vs periodic
- `TestTimerRegisters` - Register operations
- `TestTimerInterrupts` - Interrupt handling

### 5. RealTimeTimer Tests (`test_realtime_timer.py`)
Tests real-time (wall-clock) timer:
- Wall-clock timing behavior
- Frequency configuration (1-1000 Hz)
- Periodic and one-shot modes
- Register access
- Interrupt generation

**Classes:**
- `TestRTTimerBasics` - Initialization
- `TestRTTimerRegisters` - Register access
- `TestRTTimerTiming` - Wall-clock behavior (marked as slow)

### 6. Display Tests (`test_display.py`)
Tests text-mode display:
- Buffer initialization and management
- Character writing at specific positions
- Cursor positioning and advancement
- Cursor wrapping
- Display clearing and scrolling

**Classes:**
- `TestDisplayBasics` - Initialization
- `TestDisplayWriteChar` - Character writing
- `TestDisplayCursor` - Cursor operations
- `TestDisplayControl` - Clear and scroll

## Test Fixtures

### Available Fixtures (defined in `conftest.py`)

- `cpu()` - Fresh CPU instance
- `memory()` - Fresh Memory instance
- `display()` - Fresh Display instance
- `timer()` - Fresh Timer instance
- `rt_timer()` - Fresh RealTimeTimer instance
- `assembler()` - Fresh Assembler instance
- `vm()` - Fresh VirtualMachine instance
- `vm_debug()` - VM with debug enabled
- `vm_protected()` - VM with text segment protection

### Helper Functions (in `fixtures/test_helpers.py`)

```python
run_program_until_halt(vm, source, max_instructions=10000)
run_and_get_register(vm, source, register, max_instructions=10000)
run_and_get_memory(vm, source, address, size=4, max_instructions=10000)
assert_register_equals(cpu, reg, expected_value, message=None)
assert_memory_contains(memory, address, expected_value, message=None)
assert_halted(cpu, message=None)
assert_interrupt_pending(cpu, interrupt_mask, message=None)
assert_pc_equals(cpu, expected_pc, message=None)
build_program(*lines)
```

## Writing New Tests

### Test Class Template
```python
class TestFeatureName:
    """Test description"""
    
    def test_specific_behavior(self, fixture):
        """Test a specific aspect"""
        # Arrange
        setup_code()
        
        # Act
        result = action()
        
        # Assert
        assert result == expected
```

### Best Practices

1. **Use descriptive test names** - Test name should describe what is being tested
2. **One assertion per test** - Each test should verify one specific behavior
3. **Use fixtures** - Leverage pytest fixtures for clean setup
4. **Test edge cases** - Include boundary conditions and error cases
5. **Mark slow tests** - Use `@pytest.mark.slow` for tests that take >100ms
6. **Add docstrings** - Document what each test verifies
7. **Keep tests independent** - Tests should not depend on each other

### Example Test
```python
def test_counter_increments_on_tick(self, timer):
    """Test timer counter increments when enabled and ticked"""
    # Arrange - Enable timer
    timer.control = Timer.CTRL_ENABLE
    timer.compare = 100
    
    # Act - Tick once
    timer.tick()
    
    # Assert - Counter should be 1
    assert timer.counter == 1
```

## Continuous Testing

### Watch Mode (Auto-run on file changes)
```bash
uv run pytest-watch tests/unit/
```

### Run Tests on Commit (Git Hook)
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
uv run pytest tests/unit/ --tb=short
```

## Future Test Layers

The current implementation covers **Layer 1: Unit Tests**. Future additions should include:

### Layer 2: Instruction Tests
Individual instruction testing with edge cases:
- Arithmetic instructions (ADD, SUB, overflow)
- Logical instructions (AND, OR, XOR, shifts)
- Load/Store instructions (alignment, bounds)
- Branch/Jump instructions (taken/not taken)
- System instructions (HALT, WFI, MRET, CSR ops)

### Layer 3: Integration Tests
Component interaction testing:
- Timer interrupt integration with CPU
- WFI with timer interrupts
- Memory-mapped I/O integration
- Label resolution in complex programs

### Layer 4: Program Tests
Complete program execution:
- Factorial calculation
- Fibonacci sequence
- Clock program (timers + display + interrupts)
- Nested interrupt handling
- Stack operations

## Test Metrics

Current metrics (as of implementation):
- **Total Tests**: 154
- **Pass Rate**: 100%
- **Execution Time**: ~0.4 seconds
- **Code Coverage**: 55%
- **Lines of Test Code**: ~1,600
- **Test-to-Code Ratio**: ~1.2:1

## Troubleshooting

### Tests Failing After Code Changes
1. Run specific test file to isolate issue
2. Check if test assumptions still valid
3. Review code changes for breaking changes
4. Update tests if behavior intentionally changed

### Coverage Not Updating
```bash
# Clear coverage cache
rm -rf .coverage htmlcov/
uv run pytest tests/unit/ --cov=src --cov-report=html
```

### Slow Test Suite
```bash
# Run only fast tests
uv run pytest tests/unit/ -m "not slow"

# Show slowest 10 tests
uv run pytest tests/unit/ --durations=10
```

## Contributing Tests

When adding new features to the VM:

1. **Write tests first** (TDD approach)
2. **Ensure 100% pass rate** before committing
3. **Aim for >80% coverage** on new code
4. **Document complex test scenarios** with comments
5. **Update this README** with new test information

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Test Pyramid Pattern](https://martinfowler.com/articles/practical-test-pyramid.html)
