class generateName(object):
	i = 10

	def generateName(self):
		name = "?var"+ str(self.i)
		self.i += 1
		return name

def createName(string, isProp):
	if isProp:	
		name = "?p_"
	else:
		name = "?e_"
	name += string
	name = name.replace(" ", "_")
	return name

def createSelectName(start):
	return "?"+"selectVar"+str(start)

gn = generateName()
