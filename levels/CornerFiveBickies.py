# File: CornerFiveBickies.py
# -----------------------------
# Places five bickies in each corner
from game import *


# reposition Ferris to the next corner 
def move_to_next_corner() :
	move()
	move()
	move()
	turn_left()

# places 5 beepers using a for loop 
def put_five_beepers() :
	for i in range(5):
		throwup()


# Repeat once for each corner 
for i in range(4):
	put_five_beepers()
	move_to_next_corner()