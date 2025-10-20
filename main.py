#!/usr/bin/env python3
"""
Main entry point for the RISC Virtual Machine
"""

import sys
import os
import argparse

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from vm import VirtualMachine, VMError

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
    
    args = parser.parse_args()
    
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
    vm = VirtualMachine(debug=args.debug, protect_text=args.protect)
    
    try:
        # Load program
        print(f"Loading program from {args.file}...")
        vm.load_program(source)
        print(f"Loaded {len(vm.instructions)} instructions")
        
        if args.step:
            # Step-by-step execution
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
        else:
            # Run to completion
            if not args.live_display:
                print(f"\nExecuting program...")
            
            count = vm.run(
                max_instructions=args.max_instructions,
                live_display=args.live_display,
                update_interval=args.update_interval
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
