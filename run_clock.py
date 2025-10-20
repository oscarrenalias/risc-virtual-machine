#!/usr/bin/env python3
"""
Run clock.asm properly with delays to allow real-time interrupts to fire
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from vm import VirtualMachine

def main():
    # Read clock.asm
    with open('examples/clock.asm', 'r') as f:
        source = f.read()

    # Create VM
    vm = VirtualMachine(debug=False)
    vm.load_program(source)

    print("="*80)
    print("RISC-V Virtual Machine - Real-Time Clock Demo")
    print("="*80)
    print("\nRunning clock.asm with real-time timer interrupts...")
    print("The clock updates every second.")
    print("Press Ctrl+C to stop\n")

    try:
        count = 0
        last_display = 0
        
        while True:
            vm.step()
            count += 1
            
            # Add tiny delay to allow wall-clock time to pass
            # This simulates a more realistic execution speed
            time.sleep(0.0001)  # 100 microseconds per instruction
            
            # Update display every 1000 instructions
            if count - last_display >= 1000:
                print(f"\r Instructions: {count:,}  Time: {vm.cpu.registers[20]:02d}:{vm.cpu.registers[21]:02d}:{vm.cpu.registers[22]:02d}", end='', flush=True)
                last_display = count
            
            # Show full display every 10000 instructions
            if count % 10000 == 0:
                print()  # New line
                vm.display.render()
                print()

    except KeyboardInterrupt:
        print("\n\nStopped by user")

    print(f"\nFinal state:")
    print(f"  Instructions executed: {count:,}")
    print(f"  PC: 0x{vm.cpu.pc:08X}")
    print(f"  Clock: {vm.cpu.registers[20]:02d}:{vm.cpu.registers[21]:02d}:{vm.cpu.registers[22]:02d}")
    print(f"  Real-time timer: {vm.rt_timer.counter} ticks")

if __name__ == '__main__':
    main()
