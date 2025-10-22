# Current and Next Instruction Display Feature

## Overview

The CPU visualizer now displays both the **current instruction** (about to be executed) and the **next instruction** (at PC+4) in the CPU state panel during step mode and live visualization.

## Implementation

### Changes Made

1. **VirtualMachine (`src/vm.py`)**:
   - Added `get_next_instruction_text()` method
   - Returns the instruction at PC+4 (sequential next instruction)
   - Handles edge cases: halted, waiting for interrupt, end of program

2. **CPUVisualizer (`src/cpu_visualizer.py`)**:
   - Modified `render_to_string()` to accept both `show_current_instruction` and `show_next_instruction` parameters
   - Modified `render_panel()` to pass both parameters
   - Current instruction is shown in cyan, next instruction in dimmed magenta

3. **VMVisualizer (`src/visualizer.py`)**:
   - Updated `render()` to fetch both current and next instructions
   - Updated `_render_split_view()` to pass both to CPU visualizer
   - Renamed parameter from `show_next_instruction` to `show_instructions` for clarity

## Behavior

### Sequential Instructions
For most instructions (ADD, SUB, LW, SW, etc.), the next instruction shows what will execute after:
```
Current: ADDI x5, x0, 10
Next:    ADD x6, x5, x5
```

### Branch Instructions
For branches (BEQ, BNE, BLT, BGE), the next instruction shows the **sequential case** (not taken):
```
Current: BEQ x5, x6, 0x20 (+8)
Next:    ADDI x7, x0, 1
```
This is intentional to keep the implementation simple and avoid branch prediction complexity.

### Jump Instructions
For jumps (JAL, J), the next instruction shows the sequential case at PC+4:
```
Current: JAL x1, 0x100 (+64)
Next:    ADDI x8, x0, 2  [sequential, won't execute]
```

### Edge Cases

**After HALT:**
```
Current: HALT
Next:    (halted)
```

**During WFI (Wait For Interrupt):**
```
Current: ADDI x6, x0, 2
Next:    (waiting for interrupt)
```

**At End of Program:**
```
Current: ADDI x9, x0, 3
Next:    (end of program)
```

## Usage

### Step Mode
When running with `-s` flag and sufficient terminal width (≥140 columns):
```bash
uv run python main.py examples/counter.asm -s
```

The CPU panel will show:
```
╭─────────────────────── CPU State ───────────────────────╮
│ PC: 0x00000004                                          │
│ Instructions: 1                                         │
│ Status: RUNNING                                         │
│                                                         │
│ Current: ADDI t1, zero, 10                              │
│ Next: LUI a0, 0xF0000                                   │
│                                                         │
│ ═══ Registers ═══                                       │
│ ...                                                     │
╰─────────────────────────────────────────────────────────╯
```

### Live Visualization Mode
When running with `-l` flag:
```bash
uv run python main.py examples/counter.asm -l
```

During execution, you'll see the current and next instructions update in real-time (during the update intervals).

## Design Decisions

### Why Show Sequential Next Only?

We chose to always show PC+4 (sequential next) instead of predicting branch targets because:

1. **Simplicity**: No need to evaluate branch conditions or track branch prediction
2. **Consistency**: Always shows what's at PC+4, which is useful for understanding code layout
3. **Debugging**: Users can see the fallthrough case, which is helpful for debugging
4. **Performance**: No overhead from branch prediction logic

### Why Both Current and Next?

Showing both instructions provides better context:
- **Current**: What the CPU is about to execute right now
- **Next**: What comes after in memory (helps anticipate flow)

This is especially useful in step mode for understanding program flow.

## Testing

All existing tests pass (304 tests). The feature was tested with:
- Sequential instructions
- Branch instructions (taken and not taken)
- Jump instructions
- HALT instruction
- WFI instruction
- End of program scenarios

## Future Enhancements

Possible future improvements:
1. Add a small indicator `[branch]` or `[jump]` for control flow instructions
2. Optionally show both sequential and branch target for branches
3. Add instruction highlighting based on type (arithmetic, memory, control flow)
4. Show instruction count or cycles remaining for timed operations
