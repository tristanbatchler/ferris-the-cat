# File: PotholeFerris.py
# -----------------------------
# Fills the pothole beneath Ferris's current position by 
# placing a bickie on that corner. For this function to work 
# correctly, Ferris must be facing east immediately above the 
# pothole. When execution is complete, Ferris will have 
# returned to the same square and will again be facing east.

from game import *

def fill_pothole():
	turn_right()
	move()
	throwup()
	turn_around()
	move()
	turn_right()

# Turns Ferris 90 degrees to the right. 
def turn_right():
	turn_left()
	turn_left()
	turn_left()
	
# Turns Ferris around 180 degrees. 
def turn_around():
	turn_left()
	turn_left()

# Main steps. 
move()
fill_pothole()
move()
