# File: BickieLineBug.py
# ------------------------------
# Uses a while loop to place a line of bickies.
# This program works for a world of any size.
# However, because each world requires one fewer
# move() than throwup(), it always misses a bickie.
from game import *

# repeats until Ferris faces a wall
while can_move():
	# throw up on current square
	throwup()
	# move to the next square
	move()
