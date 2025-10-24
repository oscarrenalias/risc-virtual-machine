# Test character literals feature
# Tests: single chars, escape sequences, and various ASCII values
# Uses RISC-V ABI register names

.text
main:
    # Load display base address
    LUI a0, 0xF0            # a0 = 0xF0000 (display buffer base)
    
    # Test 1: Simple uppercase character
    ADDI a1, zero, 'H'      # 'H' = 72
    SW a1, 0(a0)
    
    # Test 2: Simple lowercase character
    ADDI a1, zero, 'e'      # 'e' = 101
    SW a1, 4(a0)
    
    # Test 3: Simple lowercase
    ADDI a1, zero, 'l'      # 'l' = 108
    SW a1, 8(a0)
    
    # Test 4: Same character again
    SW a1, 12(a0)           # Reuse 'l'
    
    # Test 5: Lowercase 'o'
    ADDI a1, zero, 'o'      # 'o' = 111
    SW a1, 16(a0)
    
    # Test 6: Space character
    ADDI a1, zero, ' '      # space = 32
    SW a1, 20(a0)
    
    # Test 7: Digit character
    ADDI a1, zero, '4'      # '4' = 52
    SW a1, 24(a0)
    
    # Test 8: Digit character
    ADDI a1, zero, '2'      # '2' = 50
    SW a1, 28(a0)
    
    # Test 9: Exclamation
    ADDI a1, zero, '!'      # '!' = 33
    SW a1, 32(a0)
    
    # Test 10: Escape sequence - tab (next line)
    # Position (1, 0) = row 1, col 0 = offset 80*4 = 320
    ADDI a2, zero, 320
    ADD a3, a0, a2          # a3 = display base + 320
    
    ADDI a1, zero, 'T'
    SW a1, 0(a3)
    ADDI a1, zero, 'a'
    SW a1, 4(a3)
    ADDI a1, zero, 'b'
    SW a1, 8(a3)
    ADDI a1, zero, ':'
    SW a1, 12(a3)
    ADDI a1, zero, '\t'     # Tab character (9)
    SW a1, 16(a3)
    ADDI a1, zero, 'X'
    SW a1, 20(a3)
    
    # Test 11: Escape sequence - newline indicator (row 2)
    ADDI a2, zero, 640      # Row 2 = 80*2*4 = 640
    ADD a3, a0, a2
    
    ADDI a1, zero, 'N'
    SW a1, 0(a3)
    ADDI a1, zero, 'e'
    SW a1, 4(a3)
    ADDI a1, zero, 'w'
    SW a1, 8(a3)
    ADDI a1, zero, 'l'
    SW a1, 12(a3)
    ADDI a1, zero, 'i'
    SW a1, 16(a3)
    ADDI a1, zero, 'n'
    SW a1, 20(a3)
    ADDI a1, zero, 'e'
    SW a1, 24(a3)
    ADDI a1, zero, ':'
    SW a1, 28(a3)
    ADDI a1, zero, '\n'     # Newline (10)
    SW a1, 32(a3)
    
    # Test 12: Null character (row 3)
    ADDI a2, zero, 960      # Row 3 = 80*3*4 = 960
    ADD a3, a0, a2
    
    ADDI a1, zero, 'N'
    SW a1, 0(a3)
    ADDI a1, zero, 'u'
    SW a1, 4(a3)
    ADDI a1, zero, 'l'
    SW a1, 8(a3)
    ADDI a1, zero, 'l'
    SW a1, 12(a3)
    ADDI a1, zero, ':'
    SW a1, 16(a3)
    ADDI a1, zero, '\0'     # Null character (0)
    SW a1, 20(a3)
    
    # Test 13: Quote and backslash (row 4)
    ADDI a2, zero, 1280     # Row 4 = 80*4*4 = 1280
    ADD a3, a0, a2
    
    ADDI a1, zero, 'Q'
    SW a1, 0(a3)
    ADDI a1, zero, 'u'
    SW a1, 4(a3)
    ADDI a1, zero, 'o'
    SW a1, 8(a3)
    ADDI a1, zero, 't'
    SW a1, 12(a3)
    ADDI a1, zero, 'e'
    SW a1, 16(a3)
    ADDI a1, zero, ':'
    SW a1, 20(a3)
    ADDI a1, zero, '\''     # Single quote (39)
    SW a1, 24(a3)
    ADDI a1, zero, ' '
    SW a1, 28(a3)
    ADDI a1, zero, 'B'
    SW a1, 32(a3)
    ADDI a1, zero, 's'
    SW a1, 36(a3)
    ADDI a1, zero, 'l'
    SW a1, 40(a3)
    ADDI a1, zero, 'a'
    SW a1, 44(a3)
    ADDI a1, zero, 's'
    SW a1, 48(a3)
    ADDI a1, zero, 'h'
    SW a1, 52(a3)
    ADDI a1, zero, ':'
    SW a1, 56(a3)
    ADDI a1, zero, '\\'     # Backslash (92)
    SW a1, 60(a3)
    
    HALT
