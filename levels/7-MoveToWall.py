# File: 7-MoveToWall.py
# ------------------------------
# Uses a "while" loop to move Ferris until it hits
# a wall. Works on any sized world.
from game import *

# this is a very useful function 
def move_to_wall():
	# repeat the body while the condition holds
	while can_move():
		move()

# main steps
# call the move to wall function
move_to_wall()