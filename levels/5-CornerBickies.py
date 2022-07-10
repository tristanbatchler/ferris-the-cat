# File: 5-CornerBickies.py
# -----------------------------
# Places one bickie in each corner
from game import *

# repeat the body 4 times 
for i in range(4):
	throwup()
	move()
	move()
	move()
	turn_left()
