# File: BickieEatingFerris.py
# --------------------------------
# The BickieCollectingFerris program collects all the bickies
# in a series of vertical towers and deposits them at the
# eastmost corner on 1st row.
from game import *

# Collects the bickies from every tower by moving along 1st
# row, calling collect_one_tower at every corner.  The
# postcondition for this function is that Ferris is in the
# easternmost corner of 1st row facing east.
def collect_all_bickies():
	while can_move():
		collect_one_tower()
		move()
	collect_one_tower()

# Collects the bickies in a single tower. When collect_one_tower
# is called, Ferris must be on 1st row facing east.  The
# postcondition for collect_one_tower is that Ferris must again
# be facing east on that same corner.
def collect_one_tower():
	turn_left()
	collect_line_of_bickies()
	turn_around()
	move_to_wall()
	turn_left()

# Collects a consecutive line of bickies. The end of the bickie
# line is indicated by a corner that contains no bickies.
def collect_line_of_bickies():
	while can_move():
		if bickie_here():
			eat()
		move()

# Drops all the bickies on the current corner.
def drop_all_bickies() :
	while get_bickie_count() > 0:
		throwup()

# Returns Ferris to its initial position at the corner of 1st
# Avenue and 1st row, facing east.  The precondition for this
# function is that Ferris must be facing east somewhere on 1st
# row, which is true at the conclusion of collect_all_bickies.
def return_home():
	turn_around()
	move_to_wall()
	turn_around()

# Moves Ferris forward until it is blocked by a wall.
def move_to_wall():
	while can_move():
		move()

# Turns Ferris 180 degrees around
def turn_around():
	turn_left()
	turn_left()


collect_all_bickies()
drop_all_bickies()
return_home()