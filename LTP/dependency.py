import spacy

#nlp = None
nlp = spacy.load('en')

def hasDependency(w, dep):
	for dependency in findDependencies(w):
		if dependency.dep_ == dep:
			return True
	return False

def concatDict(dict1, dict2):
	for k, v in dict2.items():
		if k in dict1:
			pass
		else:
			dict1[k] = v
	return dict1

def addIDs(result):
	i = 0
	returnResult = []
	for w in result:
		w.id = i
		returnResult.append(w)
		i += 1
	return returnResult

def getID(word, result):
	i = 0
	for w in result:
		if w == word:
			return i
		i += 1
	raise ValueError

def findRoot(result):
	for w in result:
		if w.dep_ == "ROOT":
			return w

		#print(w, ", ",w.dep_, ", ", w.head)

def findDependencies(word):
	returnList = []
	result = word.doc
	for w in result[:len(result) - 1]:
		#print(word, "'", w, ", ", w.head, ", ", w.dep_,". ")
		if w.head == word:
			#print("SELECTED '", w, "', ", w.head, ", ", w.dep_)
			returnList.append(w)
	return returnList

def createDependencyTree(sentence):
	return nlp(sentence)

def loadSpacy():
	print("Loading spacy...")
	print("Done loading spacy")
