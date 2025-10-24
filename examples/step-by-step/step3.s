# Step 3: print an entire string from data segment to screen x,y coordinates
# using a function call

.data
message: .asciiz "Hello, World!"

.text
main:

    # set up parameters
    LA a0, message
    ADDI a1, zero, 15
    ADDI a2, zero, 10

    # call the function
    CALL print_string_xy

    # stop execution and finish program
    HALT

#
# function that prints a string represented by its address on the given coordinates
# a0: string address (pointer)
# a1: x coordinate (int)
# a2: y coordinate (int)
# Uses: t0, t1
# t0: screen buffer address
# t1: character offset
# Returns: nothing
#
print_string_xy:
    # load address of screen buffer
    LUI t0, 0xF0

    # calculate starting offset: (y * 80 + x)
    ADDI t1, zero, 80
    MUL t1, a2, t1
    ADD t1, t1, a1

    # add address to offset
    ADD t0, t0, t1

print_loop:
    # print the character
    LBU t1, 0(a0)
    SB t1, 0(t0)
    # increement string pointer
    ADDI a0, a0, 1
    # increase screen buffer address
    ADDI t0, t0, 1
    # check for null terminator
    BEQ t1, zero, print_done
    # loop back
    J print_loop

    # end the code

print_done:
    RET