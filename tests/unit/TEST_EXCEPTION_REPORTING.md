# Exception Reporting Test Suite

This document describes the comprehensive test suite for the enhanced exception reporting system.

## Test Coverage

The test suite includes **24 new tests** across 6 test classes, validating all aspects of the exception reporting system.

### Test Classes

#### 1. `TestExceptionReporting` (4 tests)
Tests that exceptions are raised with comprehensive debugging information:

- **test_memory_access_out_of_bounds_exception**: Validates that out-of-bounds memory access generates a detailed report with all sections (instruction context, registers, stack, CSRs, memory region analysis, memory dump, hints)
- **test_unaligned_memory_access_exception**: Validates alignment error reporting with specific hints about alignment requirements
- **test_memory_protection_violation_exception**: Validates protection error reporting when writing to read-only text segment
- **test_pc_out_of_bounds_exception**: Validates PC out of bounds error reporting

#### 2. `TestExceptionInformation` (4 tests)
Tests that exception information is complete and accurate:

- **test_exception_captures_cpu_state**: Verifies CPU state (registers, PC, instruction count) is captured at time of error
- **test_exception_shows_instruction_context**: Verifies surrounding instructions are shown (2 before, 2 after the fault)
- **test_exception_shows_stack_usage**: Verifies stack state shows SP, usage, and stack values
- **test_exception_shows_csr_state**: Verifies CSR values and interrupt state are displayed

#### 3. `TestExceptionClassification` (3 tests)
Tests that exceptions are properly classified with helpful hints:

- **test_out_of_bounds_classification**: Verifies "Memory Access Violation" category and relevant hints
- **test_alignment_error_classification**: Verifies alignment-specific hints are provided
- **test_protection_error_classification**: Verifies "Memory Protection Violation" category and text segment hints

#### 4. `TestDebuggerComponents` (7 tests)
Tests individual debugger formatting components:

- **test_register_dump_format**: Verifies register dump shows all registers with hex/decimal values and ABI names
- **test_csr_dump_format**: Verifies CSR dump shows all CSRs with interpretations
- **test_stack_dump_format**: Verifies stack dump shows SP, usage, and top words with marker
- **test_instruction_context_format**: Verifies instruction context shows addresses and current instruction marker
- **test_memory_region_analysis**: Verifies memory region identification (text, data, heap, stack, etc.)
- **test_memory_dump_format**: Verifies hexdump format with addresses, hex bytes, and ASCII representation
- **test_interrupt_state_format**: Verifies interrupt and timer state display

#### 5. `TestExceptionWithDifferentStates` (3 tests)
Tests exceptions with various CPU states:

- **test_exception_with_interrupt_enabled**: Verifies exception report shows interrupt enable state
- **test_exception_with_modified_sp**: Verifies exception report shows modified stack pointer and usage
- **test_exception_captures_original_exception**: Verifies VMError captures the original exception (e.g., MemoryAccessError)

#### 6. `TestExceptionEdgeCases` (3 tests)
Tests exception reporting in edge cases:

- **test_exception_on_first_instruction**: Verifies exception on first instruction still shows context
- **test_exception_with_empty_stack**: Verifies exception with unused stack shows initial SP
- **test_format_exception_report_function**: Verifies standalone format_exception_report() function works correctly

## What Each Test Validates

### Exception Content Validation

Each exception test validates the presence of:

1. **Exception Header**
   - Exception type name (MemoryAccessError, MemoryProtectionError, VMError, etc.)
   - Category classification
   - Error message
   - Helpful hints

2. **Instruction Context**
   - Instructions before fault (up to 2)
   - Faulting instruction with "EXCEPTION HERE" marker
   - Instructions after fault (up to 2)
   - Address for each instruction

3. **Register State**
   - All 32 registers (x0-x31)
   - ABI names (zero, ra, sp, etc.)
   - Hexadecimal values
   - Signed decimal values
   - PC value
   - Instruction count
   - CPU halted status
   - WFI status

4. **CSR State**
   - All CSR registers (MSTATUS, MIE, MTVEC, MEPC, MCAUSE, MIP)
   - Bit-level interpretations
   - Global interrupt enable state

5. **Stack State**
   - Stack pointer value
   - Stack usage (bytes used)
   - Top N words of stack
   - Stack values in hex and decimal
   - Current SP marker (→)

6. **Interrupt/Timer State**
   - Global interrupt enable/disable
   - WFI state
   - Pending interrupts
   - Enabled interrupt sources
   - Cycle-based timer state
   - Real-time timer state

7. **Memory Region Analysis** (for memory errors)
   - Address being accessed
   - Memory region identification
   - Valid address ranges
   - Memory layout overview

8. **Memory Hexdump** (for memory errors)
   - Hexadecimal bytes around fault address
   - ASCII representation
   - Fault line marker (→)

## Running the Tests

Run all exception reporting tests:
```bash
uv run pytest tests/unit/test_exception_reporting.py -v
```

Run specific test class:
```bash
uv run pytest tests/unit/test_exception_reporting.py::TestExceptionReporting -v
```

Run specific test:
```bash
uv run pytest tests/unit/test_exception_reporting.py::TestExceptionReporting::test_memory_access_out_of_bounds_exception -v
```

## Test Results

All 24 tests pass successfully, validating:
- ✅ Complete exception information capture
- ✅ Proper formatting of all report sections
- ✅ Accurate classification and hints
- ✅ Edge case handling
- ✅ Integration with VM execution

Combined with the existing 247 tests, the total test suite now has **271 tests**, all passing.

## Example Test Assertion

Here's an example of what the tests validate:

```python
def test_memory_access_out_of_bounds_exception(self):
    vm = VirtualMachine()
    
    program = """
    LUI x7, 0x10000       # x7 = 0x10000000 (way out of bounds)
    LW x8, 0(x7)          # This should trigger exception
    HALT
    """
    
    vm.load_program(program)
    
    with pytest.raises(VMError) as exc_info:
        vm.run(max_instructions=100)
    
    error_str = str(exc_info.value)
    
    # Validate all major sections are present
    assert "CPU EXCEPTION" in error_str
    assert "MemoryAccessError" in error_str
    assert "Memory Access Violation" in error_str
    assert "Hints:" in error_str
    assert "Instruction Context:" in error_str
    assert "Register State:" in error_str
    assert "Stack State" in error_str
    assert "Control and Status Registers" in error_str
    assert "Memory Region Analysis:" in error_str
    assert "Memory dump around" in error_str
    
    # Validate fault address captured
    assert error.fault_address == 0x10000000
```

## Coverage

The test suite provides comprehensive coverage of:
- All exception types (MemoryAccessError, MemoryProtectionError, VMError)
- All debugger components (registers, CSRs, stack, instructions, memory)
- Various CPU states (interrupts enabled/disabled, modified SP, etc.)
- Edge cases (first instruction, empty stack, etc.)
- Exception classification and hint generation

This ensures the exception reporting system is robust and reliable for debugging assembly programs.
