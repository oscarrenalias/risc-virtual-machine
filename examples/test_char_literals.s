# Test character literals feature
# Tests: single chars, escape sequences, and various ASCII values

.text
main:
    # Load display base address
    LUI x10, 0xF0           # x10 = 0xF0000 (display buffer base)
    
    # Test 1: Simple uppercase character
    ADDI x11, x0, 'H'       # 'H' = 72
    SW x11, 0(x10)
    
    # Test 2: Simple lowercase character
    ADDI x11, x0, 'e'       # 'e' = 101
    SW x11, 4(x10)
    
    # Test 3: Simple lowercase
    ADDI x11, x0, 'l'       # 'l' = 108
    SW x11, 8(x10)
    
    # Test 4: Same character again
    SW x11, 12(x10)         # Reuse 'l'
    
    # Test 5: Lowercase 'o'
    ADDI x11, x0, 'o'       # 'o' = 111
    SW x11, 16(x10)
    
    # Test 6: Space character
    ADDI x11, x0, ' '       # space = 32
    SW x11, 20(x10)
    
    # Test 7: Digit character
    ADDI x11, x0, '4'       # '4' = 52
    SW x11, 24(x10)
    
    # Test 8: Digit character
    ADDI x11, x0, '2'       # '2' = 50
    SW x11, 28(x10)
    
    # Test 9: Exclamation
    ADDI x11, x0, '!'       # '!' = 33
    SW x11, 32(x10)
    
    # Test 10: Escape sequence - tab (next line)
    # Position (1, 0) = row 1, col 0 = offset 80*4 = 320
    ADDI x12, x0, 320
    ADD x13, x10, x12       # x13 = display base + 320
    
    ADDI x11, x0, 'T'
    SW x11, 0(x13)
    ADDI x11, x0, 'a'
    SW x11, 4(x13)
    ADDI x11, x0, 'b'
    SW x11, 8(x13)
    ADDI x11, x0, ':'
    SW x11, 12(x13)
    ADDI x11, x0, '\t'      # Tab character (9)
    SW x11, 16(x13)
    ADDI x11, x0, 'X'
    SW x11, 20(x13)
    
    # Test 11: Escape sequence - newline indicator (row 2)
    ADDI x12, x0, 640       # Row 2 = 80*2*4 = 640
    ADD x13, x10, x12
    
    ADDI x11, x0, 'N'
    SW x11, 0(x13)
    ADDI x11, x0, 'e'
    SW x11, 4(x13)
    ADDI x11, x0, 'w'
    SW x11, 8(x13)
    ADDI x11, x0, 'l'
    SW x11, 12(x13)
    ADDI x11, x0, 'i'
    SW x11, 16(x13)
    ADDI x11, x0, 'n'
    SW x11, 20(x13)
    ADDI x11, x0, 'e'
    SW x11, 24(x13)
    ADDI x11, x0, ':'
    SW x11, 28(x13)
    ADDI x11, x0, '\n'      # Newline (10)
    SW x11, 32(x13)
    
    # Test 12: Null character (row 3)
    ADDI x12, x0, 960       # Row 3 = 80*3*4 = 960
    ADD x13, x10, x12
    
    ADDI x11, x0, 'N'
    SW x11, 0(x13)
    ADDI x11, x0, 'u'
    SW x11, 4(x13)
    ADDI x11, x0, 'l'
    SW x11, 8(x13)
    ADDI x11, x0, 'l'
    SW x11, 12(x13)
    ADDI x11, x0, ':'
    SW x11, 16(x13)
    ADDI x11, x0, '\0'      # Null character (0)
    SW x11, 20(x13)
    
    # Test 13: Quote and backslash (row 4)
    ADDI x12, x0, 1280      # Row 4 = 80*4*4 = 1280
    ADD x13, x10, x12
    
    ADDI x11, x0, 'Q'
    SW x11, 0(x13)
    ADDI x11, x0, 'u'
    SW x11, 4(x13)
    ADDI x11, x0, 'o'
    SW x11, 8(x13)
    ADDI x11, x0, 't'
    SW x11, 12(x13)
    ADDI x11, x0, 'e'
    SW x11, 16(x13)
    ADDI x11, x0, ':'
    SW x11, 20(x13)
    ADDI x11, x0, '\''      # Single quote (39)
    SW x11, 24(x13)
    ADDI x11, x0, ' '
    SW x11, 28(x13)
    ADDI x11, x0, 'B'
    SW x11, 32(x13)
    ADDI x11, x0, 's'
    SW x11, 36(x13)
    ADDI x11, x0, 'l'
    SW x11, 40(x13)
    ADDI x11, x0, 'a'
    SW x11, 44(x13)
    ADDI x11, x0, 's'
    SW x11, 48(x13)
    ADDI x11, x0, 'h'
    SW x11, 52(x13)
    ADDI x11, x0, ':'
    SW x11, 56(x13)
    ADDI x11, x0, '\\'      # Backslash (92)
    SW x11, 60(x13)
    
    HALT
