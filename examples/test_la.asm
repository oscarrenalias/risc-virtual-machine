# Test LA (Load Address) pseudo-instruction with ABI register names

.data
test_data: .word 0x12345678
test_string: .string "Test"

.text
main:
    # Test LA with data label
    LA a0, test_data        # Should load 0x10000 into a0
    LA a1, test_string      # Should load 0x10004 into a1
    
    # Verify by loading the actual values
    LW t0, 0(a0)            # Load word from test_data
    LBU t1, 0(a1)           # Load first byte from test_string ('T' = 0x54)
    
    HALT
