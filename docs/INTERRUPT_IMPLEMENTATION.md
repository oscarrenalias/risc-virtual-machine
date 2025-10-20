# Timer Interrupt Implementation Summary

## Overview

Successfully implemented a complete hardware timer interrupt system for the RISC Virtual Machine, following RISC-V interrupt handling conventions.

## Components Implemented

### 1. Timer Hardware (`src/timer.py`)
- 32-bit counter that increments each instruction cycle
- 32-bit compare register for interrupt threshold
- Control register with enable, mode, pending, and auto-reload flags
- Prescaler support for clock division
- Periodic and one-shot modes

### 2. CPU Interrupt Support (`src/cpu.py`)
- Control and Status Registers (CSRs):
  - `mstatus` (0x300) - Machine status with global interrupt enable
  - `mie` (0x304) - Interrupt enable register
  - `mtvec` (0x305) - Trap vector base address
  - `mepc` (0x341) - Exception PC (saved during interrupt)
  - `mcause` (0x342) - Trap cause register
  - `mip` (0x344) - Interrupt pending flags
- Interrupt handling methods:
  - `enter_interrupt()` - Save state and jump to handler
  - `return_from_interrupt()` - Restore state (for MRET)
  - `has_pending_interrupts()` - Check for pending interrupts
  - `get_highest_priority_interrupt()` - Priority resolution
- CSR read/write/set/clear operations

### 3. Memory-Mapped Timer Registers (`src/memory.py`)
- Timer registers at 0xF7E00-0xF7E10:
  - 0xF7E00: TIMER_COUNTER (R/W)
  - 0xF7E04: TIMER_COMPARE (R/W)
  - 0xF7E08: TIMER_CONTROL (R/W)
  - 0xF7E0C: TIMER_PRESCALER (R/W)
  - 0xF7E10: TIMER_STATUS (R)
- Automatic routing of memory accesses to timer hardware

### 4. CSR Instructions (`src/instruction.py`, `src/assembler.py`, `src/vm.py`)
- `CSRRW rd, csr, rs1` - Atomic read/write
- `CSRRS rd, csr, rs1` - Atomic read and set bits
- `CSRRC rd, csr, rs1` - Atomic read and clear bits
- `CSRRWI rd, csr, imm` - Read/write with 5-bit immediate
- `CSRRSI rd, csr, imm` - Read and set bits with immediate
- `CSRRCI rd, csr, imm` - Read and clear bits with immediate
- `MRET` - Return from interrupt handler

### 5. VM Interrupt Integration (`src/vm.py`)
- Timer ticks on every instruction cycle
- Interrupt checking before instruction fetch
- Automatic entry to interrupt handler when conditions met
- Proper PC saving and restoration

## How It Works

### Interrupt Flow

1. **Setup Phase**:
   - Program sets `mtvec` CSR to point to interrupt handler
   - Timer configured via memory-mapped registers
   - Timer interrupt enabled in `mie` register
   - Global interrupts enabled in `mstatus`

2. **Operation**:
   - Timer counter increments each instruction
   - When `counter >= compare`, interrupt fires
   - CPU checks for pending interrupts before each instruction
   - If interrupt pending and enabled, CPU enters interrupt handler

3. **Interrupt Entry**:
   - Current PC saved to `mepc`
   - Interrupt cause written to `mcause`
   - Global interrupts disabled
   - PC set to address in `mtvec`

4. **Handler Execution**:
   - User code handles the interrupt
   - Must clear timer pending bit by writing to TIMER_CONTROL
   - Must restore any modified registers
   - Executes `MRET` to return

5. **Interrupt Return**:
   - PC restored from `mepc`
   - Interrupts re-enabled
   - Execution continues from interrupted code

## Timer Control Register

Bits:
- Bit 0: **ENABLE** - Enable timer
- Bit 1: **MODE** - 0=one-shot, 1=periodic
- Bit 2: **INT_PENDING** - Write 1 to clear (write-1-to-clear)
- Bit 3: **AUTO_RELOAD** - Auto-reload counter in periodic mode

**Important**: When clearing the interrupt, write ALL control bits including
the pending bit (e.g., `0x0F` for enabled+periodic+pending+auto-reload). This
ensures the timer remains configured while clearing the interrupt.

## Example Programs

### timer_test.asm
Simple test that counts 5 timer interrupts and halts. Demonstrates:
- CSR setup
- Timer configuration (100 instruction period)
- Interrupt handler with counter increment
- Proper interrupt clearing

### timer_basic.asm
More complex example showing:
- Display updates driven by timer
- Main loop running alongside interrupts
- Counter display on screen

### mret_test.asm
Tests the MRET instruction in isolation

### timer_minimal.asm
Minimal setup for testing interrupt configuration

## Testing Results

✅ Timer hardware ticks correctly
✅ Compare match generates interrupts
✅ Periodic mode with auto-reload works
✅ CSR instructions read/write correctly
✅ MRET restores PC and re-enables interrupts
✅ Full interrupt flow works end-to-end
✅ Example program counts 5 interrupts and halts successfully

## Key Design Decisions

1. **Instruction-based timing**: Timer increments per instruction, not real-time.
   This makes execution deterministic and testable.

2. **Write-1-to-clear**: INT_PENDING bit follows hardware convention of writing
   1 to clear, preventing accidental clears.

3. **No nested interrupts**: Interrupts disabled during handler execution for
   simplicity. Can be extended later if needed.

4. **RISC-V CSR model**: Follows standard RISC-V interrupt architecture for
   compatibility and familiarity.

5. **Memory-mapped timer**: Hardware timer accessible via standard memory
   operations, no special instructions needed.

## Future Enhancements

Potential additions:
- Multiple interrupt sources (keyboard, display v-blank, etc.)
- Interrupt priorities
- Nested interrupt support
- Real-time mode (wall-clock based timing)
- Watchdog timer
- Software interrupts (ECALL)
- Exception handling (invalid instruction, memory access violations)

## Files Modified/Created

**New Files**:
- `src/timer.py` - Timer hardware implementation
- `examples/timer_test.asm` - Simple interrupt test
- `examples/timer_basic.asm` - Display-driven example
- `examples/mret_test.asm` - MRET instruction test
- `examples/timer_minimal.asm` - Minimal setup test

**Modified Files**:
- `src/cpu.py` - Added CSRs and interrupt handling
- `src/memory.py` - Added timer memory-mapped registers
- `src/vm.py` - Integrated timer and interrupt checking
- `src/instruction.py` - Added CSR instructions and MRET
- `src/assembler.py` - Added CSR instruction parsing
- `README.md` - Documented timer and interrupt features

## Conclusion

The timer interrupt system is fully functional and provides a solid foundation
for more advanced features like multitasking, real-time event handling, and
system calls. The implementation follows industry-standard RISC-V conventions,
making it familiar to developers with embedded systems experience.
