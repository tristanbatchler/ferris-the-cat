# File: 9-BickieLine.py
# ------------------------------
# Uses a while loop to place a line of bickies.
# This program works for a world of any size.
from game import *

# repeats until karel faces a wall
while can_move():
	# place a beeper on current square
	throwup()
	# move to the next square
	move()

# solves the fencepost bug (OBOB)
throwup()

