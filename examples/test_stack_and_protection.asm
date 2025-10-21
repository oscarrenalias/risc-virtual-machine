# Test program to show stack usage and then trigger write protection error
# This demonstrates better stack state in the error report

# Push some values onto the stack
ADDI x5, x0, 100      # x5 = 100
ADDI x2, x2, -4       # Move SP down (allocate 4 bytes)
SW x5, 0(x2)          # Store value on stack

ADDI x6, x0, 200      # x6 = 200
ADDI x2, x2, -4       # Allocate more
SW x6, 0(x2)          # Store another value

ADDI x7, x0, 300      # x7 = 300
ADDI x2, x2, -4       # Allocate more
SW x7, 0(x2)          # Store another value

# Now try to write to text segment (should fail with protection enabled)
ADDI x8, x0, 0        # x8 = 0 (text segment address)
SW x5, 0(x8)          # This should trigger: Memory Protection Violation

HALT
