from game import *

# eats a bickie if one is present 
# throws up a bickie otherwise 
def invert_bickie():
	# an if/else statement 
	if bickie_here():
		eat()
	else:
		throwup()


# the main steps
while can_move(): 
	invert_bickie()
	move()
# to prevent a fencepost bug 
invert_bickie()

