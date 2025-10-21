# CPU Clock Feature

## Overview

The RISC VM includes a configurable CPU clock that simulates real processor execution speed. This feature helps users understand the impact of code optimization and CPU frequency on program execution time.

## Features

- **Configurable frequency**: 1 Hz to 10 kHz (default: 1000 Hz / 1 kHz)
- **Disable option**: Run at maximum speed for testing/benchmarking
- **Timer compatible**: Both cycle-based and real-time timers work correctly with clock
- **WFI support**: Clock continues ticking during Wait-For-Interrupt state
- **Adaptive display updates**: At low clock speeds, live display updates every instruction for better visibility

## Usage

### Command Line

```bash
# Run with default 1 kHz clock (1ms per instruction)
./run.sh examples/hello.asm

# Run at 100 Hz (10ms per instruction)
./run.sh examples/hello.asm --clock-hz 100

# Run at 10 kHz (0.1ms per instruction)
./run.sh examples/hello.asm --clock-hz 10000

# Disable clock for maximum speed
./run.sh examples/hello.asm --no-clock

# Very slow execution (1 instruction per second!)
./run.sh examples/hello.asm --clock-hz 1
```

### Python API

```python
from src import VirtualMachine

# Create VM with custom clock frequency
vm = VirtualMachine(cpu_clock_hz=1000, enable_clock=True)
vm.load_program(source)
vm.run()

# Create VM without clock (max speed)
vm = VirtualMachine(enable_clock=False)
vm.load_program(source)
vm.run()

# Change clock frequency at runtime
vm.cpu_clock.frequency = 500  # 500 Hz
vm.cpu_clock.disable()  # Disable clock
vm.cpu_clock.enable()  # Re-enable clock
```

## Educational Use Cases

### 1. Understanding CPU Speed Impact

```bash
# Compare execution times with different clock speeds
time ./run.sh examples/fibonacci.asm --clock-hz 10000 --no-display
time ./run.sh examples/fibonacci.asm --clock-hz 1000 --no-display
time ./run.sh examples/fibonacci.asm --clock-hz 100 --no-display

# Watch execution in slow motion with live display
./run.sh examples/counter.asm --clock-hz 5 -l
./run.sh examples/counter.asm --clock-hz 1 -l  # 1 instruction per second!
```

### 2. Code Optimization Demonstration

Run an optimized vs unoptimized algorithm at low clock speeds to visualize the difference:

```bash
# Slow enough to see the difference
./run.sh examples/optimized.asm --clock-hz 10
./run.sh examples/unoptimized.asm --clock-hz 10
```

### 3. Real-Time Programming

The CPU clock works seamlessly with real-time timers:

```bash
# 100 Hz CPU with 1 Hz real-time timer
./run.sh examples/timer_demo.asm --clock-hz 100
```

## Implementation Details

### Clock Module

The `CPUClock` class in `src/cpu_clock.py`:
- Uses `time.perf_counter()` for high-resolution timing
- Uses `time.sleep()` to enforce cycle delays
- Automatically adjusts for clock drift
- Minimal overhead when disabled

### Integration

The clock is integrated into the VM's `step()` method:
1. Execute instruction
2. Call `cpu_clock.tick()` to enforce timing
3. Timers continue to work (cycle-based and real-time)
4. WFI state respects clock timing

In live display mode, the update interval is automatically adjusted based on clock speed:
- **≤10 Hz**: Update every instruction (you see each change)
- **≤100 Hz**: Update every 10 instructions
- **≤1000 Hz**: Update every 100 instructions
- **>1000 Hz or disabled**: Use default interval (10,000 instructions)

This ensures smooth visual feedback at all clock speeds.

### Accuracy

- **Not cycle-accurate**: Python's `time.sleep()` has ~1ms resolution
- **Good enough for educational purposes**: Demonstrates concepts clearly
- **Higher frequencies (>5kHz)**: May not be perfectly accurate due to Python overhead
- **Lower frequencies (<100 Hz)**: Very accurate timing

## Design Decisions

1. **Default 1 kHz**: Good balance between speed and visibility
2. **Sleep-based timing**: Simpler than busy-wait, good enough for purpose
3. **Disable option**: Essential for testing and maximum-speed execution
4. **Timer compatibility**: Both timer types work correctly with clock
5. **No breaking changes**: Existing code works without modification

## Examples

### Example 1: Slow Motion Execution

Watch your program execute one instruction per second:

```bash
./run.sh examples/hello.asm --clock-hz 1 -l
```

### Example 2: Performance Comparison

```bash
# Fast execution
time ./run.sh examples/prime_check.asm --clock-hz 10000 --no-display

# Maximum speed
time ./run.sh examples/prime_check.asm --no-clock --no-display
```

### Example 3: Interactive Debugging at Human Speed

```bash
# Run at 10 Hz so you can follow along
./run.sh examples/test.asm --clock-hz 10 -l --cpu-view
```

## Notes

- Clock timing is enforced in `VirtualMachine.step()` after each instruction
- WFI state: Clock continues ticking (allows timers to fire)
- Maximum speed: Use `--no-clock` for testing or benchmarking
- The clock.asm example has a pre-existing alignment bug (unrelated to CPU clock)

## Future Enhancements

Potential improvements:
- Cycle-accurate timing option
- Dynamic frequency scaling
- Instruction-level profiling with timing
- Clock statistics (actual vs target frequency)
