# Bouncing Ball Demo
# A ball (represented by 'O') bounces around the screen
# Display is 80 columns x 25 rows
# Ball bounces off all 4 edges and continues forever

# Memory-mapped display starts at 0xF0000
# Display is 80x25 = 2000 characters (0x7D0 bytes)
# Each position is 1 byte (ASCII character)

# Register usage (ABI names):
# s0 - current X position (column: 0-79)
# s1 - current Y position (row: 0-24)
# s2 - X velocity (-1 = left, 1 = right)
# s3 - Y velocity (-1 = up, 1 = down)
# t0 - temporary calculations
# t1 - temporary calculations
# t2 - display base address
# a0 - character to display

main:
    # Initialize display base address
    # 0xF0000 = upper 20 bits: 0x000F0, lower 12 bits: 0x000
    lui t2, 0xF0             # Load upper immediate: t2 = 0xF0000
    
    # Clear the screen first
    call clear_screen
    
    # Initialize ball position (center of screen)
    addi s0, zero, 40        # X position = 40 (middle column)
    addi s1, zero, 12        # Y position = 12 (middle row)
    
    # Initialize velocity (moving down-right)
    addi s2, zero, 1         # X velocity = 1 (moving right)
    addi s3, zero, 1         # Y velocity = 1 (moving down)

game_loop:
    # Erase ball at current position
    add t0, zero, s0         # t0 = X position
    add t1, zero, s1         # t1 = Y position
    addi a0, zero, 32        # a0 = space character (ASCII 32)
    call draw_char
    
    # Update X position
    add s0, s0, s2           # X = X + velocity_x
    
    # Check left edge (X < 0)
    blt s0, zero, bounce_left
    
    # Check right edge (X >= 80)
    addi t0, zero, 80
    bge s0, t0, bounce_right
    jal zero, check_y

bounce_left:
    addi s0, zero, 0         # Set X = 0
    addi s2, zero, 1         # Reverse velocity (move right)
    jal zero, check_y

bounce_right:
    addi s0, zero, 79        # Set X = 79
    addi t0, zero, -1
    add s2, zero, t0         # Reverse velocity (move left)

check_y:
    # Update Y position
    add s1, s1, s3           # Y = Y + velocity_y
    
    # Check top edge (Y < 0)
    blt s1, zero, bounce_top
    
    # Check bottom edge (Y >= 25)
    addi t0, zero, 25
    bge s1, t0, bounce_bottom
    jal zero, draw_ball

bounce_top:
    addi s1, zero, 0         # Set Y = 0
    addi s3, zero, 1         # Reverse velocity (move down)
    jal zero, draw_ball

bounce_bottom:
    addi s1, zero, 24        # Set Y = 24
    addi t0, zero, -1
    add s3, zero, t0         # Reverse velocity (move up)

draw_ball:
    # Draw ball at new position
    add t0, zero, s0         # t0 = X position
    add t1, zero, s1         # t1 = Y position
    addi a0, zero, 79        # a0 = 'O' character (ASCII 79)
    call draw_char
    
    # Add delay to make movement visible
    call delay
    
    # Loop forever
    jal zero, game_loop

# Function: draw_char
# Draw a character at position (t0, t1)
# Parameters:
#   t0 = X position (column)
#   t1 = Y position (row)
#   a0 = character to draw
#   t2 = display base address
# Returns: none
draw_char:
    # Calculate offset: offset = (Y * 80) + X
    addi t3, zero, 80        # t3 = 80 (columns per row)
    mul t4, t1, t3           # t4 = Y * 80
    add t4, t4, t0           # t4 = (Y * 80) + X
    
    # Calculate memory address
    add t4, t2, t4           # t4 = base + offset
    
    # Write character to display
    sb a0, 0(t4)             # Store byte at calculated address
    
    # Return
    ret

# Function: clear_screen
# Clear the entire screen by writing spaces
# Parameters:
#   t2 = display base address
# Returns: none
clear_screen:
    addi t0, zero, 0         # t0 = counter (0 to 2000)
    addi t1, zero, 2000      # t1 = total characters (80 * 25)
    addi a0, zero, 32        # a0 = space character

clear_loop:
    bge t0, t1, clear_done   # if counter >= 2000, done
    
    add t3, t2, t0           # t3 = base + offset
    sb a0, 0(t3)             # Write space
    
    addi t0, t0, 1           # counter++
    jal zero, clear_loop

clear_done:
    ret                      # Return

# Function: delay
# Simple delay loop to slow down the animation
# Parameters: none
# Returns: none
delay:
    addi t5, zero, 0         # t5 = outer loop counter
    addi t6, zero, 50        # t6 = outer loop iterations

delay_outer:
    bge t5, t6, delay_done   # if outer >= 50, done
    
    addi a1, zero, 0         # a1 = inner loop counter
    addi a2, zero, 5000      # a2 = inner loop iterations
    
delay_inner:
    bge a1, a2, delay_outer_next  # if inner >= 5000, next outer
    addi a1, a1, 1           # inner++
    jal zero, delay_inner

delay_outer_next:
    addi t5, t5, 1           # outer++
    jal zero, delay_outer

delay_done:
    ret                      # Return

# Program should never reach here, but halt just in case
halt
