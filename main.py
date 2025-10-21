#!/usr/bin/env python3
"""
Main entry point for the RISC Virtual Machine
"""

import sys
import os
import argparse
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src import VirtualMachine, VMError, VMVisualizer


def run_visual_step_mode(vm, visualizer, args):
    """
    Run step mode with visual panels showing CPU state
    
    Args:
        vm: VirtualMachine instance
        visualizer: VMVisualizer instance
        args: Command-line arguments
    """
    visualizer.print_info("Visual step mode - CPU state panel enabled")
    
    continuous_mode = False
    
    while not vm.cpu.halted:
        # Render current state
        visualizer.render_step_mode(show_commands=True)
        
        if continuous_mode:
            # In continuous mode, just step automatically
            vm.step()
            # Check for breakpoints (future enhancement)
            continue
        
        # Get command from user
        cmd = input(f"\n[0x{vm.cpu.pc:08X}]> ").strip().lower()
        
        if cmd == 'q':
            break
        elif cmd == 's' or cmd == '':
            # Step: execute one instruction
            vm.step()
        elif cmd == 'c':
            # Continue: run continuously
            continuous_mode = True
            visualizer.print_info("Continuous mode - running until halt or breakpoint")
        elif cmd == 'r':
            # Show registers (already shown in panel, but provide explicit dump)
            vm.dump_state()
            input("\nPress Enter to continue...")
        elif cmd == 'd':
            # Show display only
            vm.display.render()
            input("\nPress Enter to continue...")
        elif cmd.startswith('m '):
            # Show memory at address
            try:
                addr = int(cmd[2:], 0)
                print(vm.memory.dump(addr, 128))
                input("\nPress Enter to continue...")
            except ValueError:
                visualizer.print_error("Invalid address format")
        elif cmd.startswith('b '):
            # Set breakpoint (placeholder for future)
            try:
                addr = int(cmd[2:], 0)
                vm.add_breakpoint(addr)
                visualizer.print_info(f"Breakpoint set at 0x{addr:08X}")
            except ValueError:
                visualizer.print_error("Invalid address format")
        else:
            visualizer.print_error("Unknown command")
    
    visualizer.print_info("Execution completed or halted")


def run_text_step_mode(vm, args):
    """
    Run original text-based step mode (fallback)
    
    Args:
        vm: VirtualMachine instance
        args: Command-line arguments
    """
    print("\nStep-by-step execution. Commands:")
    print("  [Enter] - Execute next instruction")
    print("  r - Show registers")
    print("  d - Show display")
    print("  m <addr> - Show memory at address")
    print("  q - Quit")
    
    while not vm.cpu.halted:
        cmd = input(f"\n[0x{vm.cpu.pc:08X}]> ").strip().lower()
        
        if cmd == 'q':
            break
        elif cmd == 'r':
            vm.dump_state()
        elif cmd == 'd':
            vm.display.render()
        elif cmd.startswith('m '):
            try:
                addr = int(cmd[2:], 0)
                print(vm.memory.dump(addr, 128))
            except ValueError:
                print("Invalid address")
        elif cmd == '':
            vm.step()
            if not args.no_display:
                vm.display.render_simple()
        else:
            print("Unknown command")


def main():
    parser = argparse.ArgumentParser(description='RISC Virtual Machine')
    parser.add_argument('file', help='Assembly source file to execute')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    parser.add_argument('-s', '--step', action='store_true', help='Step through execution')
    parser.add_argument('-p', '--protect', action='store_true', help='Protect text segment')
    parser.add_argument('-m', '--max-instructions', type=int, default=1000000,
                       help='Maximum instructions to execute (default: 1000000)')
    parser.add_argument('--no-display', action='store_true', help='Disable display rendering')
    parser.add_argument('-l', '--live-display', action='store_true', 
                       help='Update display in real-time during execution')
    parser.add_argument('--update-interval', type=int, default=10000,
                       help='Instructions between display updates in live mode (default: 10000)')
    parser.add_argument('--cpu-view', action='store_true',
                       help='Show CPU state panel alongside display (requires wide terminal)')
    parser.add_argument('--min-width', type=int, default=140,
                       help='Minimum terminal width for CPU view (default: 140)')
    parser.add_argument('--clock-hz', type=int, default=1000,
                       help='CPU clock frequency in Hz (1-10000, default: 1000)')
    parser.add_argument('--no-clock', action='store_true',
                       help='Disable CPU clock for maximum speed execution')
    
    args = parser.parse_args()
    
    # Configure logging based on debug flag
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(name)s] %(message)s'
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s'
        )
    
    # Read source file
    try:
        with open(args.file, 'r') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1
    
    # Create and configure VM
    enable_clock = not args.no_clock
    vm = VirtualMachine(
        debug=args.debug, 
        protect_text=args.protect,
        cpu_clock_hz=args.clock_hz,
        enable_clock=enable_clock
    )
    
    # Print clock info if enabled
    if enable_clock and not args.debug:
        print(f"CPU clock: {args.clock_hz} Hz ({1000.0/args.clock_hz:.3f} ms per instruction)")
    elif not enable_clock:
        print("CPU clock: disabled (maximum speed)")
    
    try:
        # Load program
        print(f"Loading program from {args.file}...")
        vm.load_program(source)
        print(f"Loaded {len(vm.instructions)} instructions")
        
        # Create visualizer if CPU view is requested
        visualizer = None
        if args.cpu_view or args.step:
            visualizer = VMVisualizer(vm, show_cpu=True, min_width=args.min_width)
            if visualizer.print_terminal_warning():
                print()  # Extra line after warning
        
        if args.step:
            # Step-by-step execution with new visualizer
            if visualizer and visualizer.can_show_split:
                # Use new visual step mode
                run_visual_step_mode(vm, visualizer, args)
            else:
                # Fall back to old text-based step mode
                run_text_step_mode(vm, args)
        else:
            # Run to completion
            if not args.live_display:
                print(f"\nExecuting program...")
            
            count = vm.run(
                max_instructions=args.max_instructions,
                live_display=args.live_display,
                update_interval=args.update_interval,
                visualizer=visualizer
            )
            
            if not args.live_display:
                print(f"\nExecution completed:")
                print(f"  Instructions executed: {count}")
                print(f"  Final PC: 0x{vm.cpu.pc:08X}")
            else:
                # In live mode, show final stats after display
                print(f"\n\nExecution completed:")
                print(f"  Instructions executed: {count}")
                print(f"  Final PC: 0x{vm.cpu.pc:08X}")
            
            if args.debug:
                vm.dump_state()
            
            if not args.no_display and not args.live_display:
                print("\nDisplay output:")
                vm.display.render()
    
    except VMError as e:
        print(f"\nVM Error: {e}", file=sys.stderr)
        if args.debug:
            vm.dump_state()
        return 1
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user")
        if args.debug:
            vm.dump_state()
        if not args.no_display:
            vm.display.render()
        return 130
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
