# Pattern Display Demo
# Demonstrates memory-mapped display by creating a pattern
# Uses RISC-V ABI register names and character literals

.text
main:
    # Load display base address
    LUI a0, 0xF0            # a0 = 0xF0000 (display buffer start)
    
    # Pattern: "***  RISC-VM  ***"
    
    # Write asterisks
    ADDI a1, zero, '*'
    SW a1, 0(a0)
    SW a1, 4(a0)
    SW a1, 8(a0)
    
    # Spaces
    ADDI a1, zero, ' '
    SW a1, 12(a0)
    SW a1, 16(a0)
    
    # Write "RISC-VM"
    ADDI a1, zero, 'R'
    SW a1, 20(a0)
    ADDI a1, zero, 'I'
    SW a1, 24(a0)
    ADDI a1, zero, 'S'
    SW a1, 28(a0)
    ADDI a1, zero, 'C'
    SW a1, 32(a0)
    ADDI a1, zero, '-'
    SW a1, 36(a0)
    ADDI a1, zero, 'V'
    SW a1, 40(a0)
    ADDI a1, zero, 'M'
    SW a1, 44(a0)
    
    # More spaces
    ADDI a1, zero, ' '
    SW a1, 48(a0)
    SW a1, 52(a0)
    
    # More asterisks
    ADDI a1, zero, '*'
    SW a1, 56(a0)
    SW a1, 60(a0)
    SW a1, 64(a0)
    
    # Move to next line (80 chars * 4 bytes = 320 = 0x140)
    ADDI a0, a0, 320
    
    # Second line: "32-bit Architecture"
    ADDI a1, zero, '3'
    SW a1, 0(a0)
    ADDI a1, zero, '2'
    SW a1, 4(a0)
    ADDI a1, zero, '-'
    SW a1, 8(a0)
    ADDI a1, zero, 'b'
    SW a1, 12(a0)
    ADDI a1, zero, 'i'
    SW a1, 16(a0)
    ADDI a1, zero, 't'
    SW a1, 20(a0)
    ADDI a1, zero, ' '
    SW a1, 24(a0)
    ADDI a1, zero, 'A'
    SW a1, 28(a0)
    ADDI a1, zero, 'r'
    SW a1, 32(a0)
    ADDI a1, zero, 'c'
    SW a1, 36(a0)
    ADDI a1, zero, 'h'
    SW a1, 40(a0)
    
    HALT
