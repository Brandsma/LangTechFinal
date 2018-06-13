import sys
import gc
import re
from answer import *
from dependency import loadSpacy, createDependencyTree

for line in sys.stdin:
	m = re.search("(.*)\t(.*)", line)
	string = m.group(1)
	answers = answer(m.group(2))
	if len(answers) == 0:
		string += "\tCould not find an answer."
	else:
		for a in answers:
			string += "\t" + a
	print(string)
	
