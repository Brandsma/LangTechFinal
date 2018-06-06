import sys
import gc
from answer import *
from dependency import loadSpacy, createDependencyTree

gc.collect()
loadSpacy()
for line in sys.stdin:
	print(createDependencyTree(line)[0].dep_)
	#try:
	answers = answer(line)
	if len(answers) == 0:
		print("Could not find an answer.")
	else:
		for a in answers:
			print(a) 
	#except Exception:
	#	print("I could not find an answer. Please ask a proper question!")
