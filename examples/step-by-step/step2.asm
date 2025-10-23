# Step 2: print a character c on the screen buffer based on the x,y coordinates
# using a function call

.text:
main:

    # set up parameters
    ADDI a0, zero, 15
    ADDI a1, zero, 10
    ADDI a2, zero, 'A'

    # call the function
    CALL print_character_xy

    # stop execution and finish program
    HALT

#
# function that prints a character on the given coordinates
# a0: x coordinate (int)
# a1: y coordinate (int)
# a2: character (byte)
#
print_character_xy:
    # load address of screen buffer
    LUI t0, 0xF0

    # calculate offset: (y * 80 + x)
    ADDI t1, zero, 80
    MUL t1, a1, t1
    ADD t1, t1, a0

    # add address to offset
    ADD t0, t0, t1

    # print the character
    SB a2, 0(t0)

    # end the code
    RET