# File: BickiePickingFerris.py
# -----------------------------
# The BickiePickingFerris program defines a turn_right 
# function which allows Ferris to move forward one block, 
# pick up a  bickie and then put it on the ledge.
from game import *

def turn_right():
	turn_left()
	turn_left()
	turn_left()

move()
eat()
move()
turn_left()
move()
move()
turn_right()
move()
move()
throwup()
move()
