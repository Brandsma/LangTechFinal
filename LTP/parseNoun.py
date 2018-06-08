import spacy
import traceback

from dependency import *
from find import *
from generateName import *

countWords = []
questionWords = ["what", "who", "which", "how"]

def parsePrep(word, var, prop):
	rel = word.doc
	print("Prep: " + word.text)
	print("Sentence: " + rel.text)
	varToBeShown = []
	statement = ""
	replaceDictionary = {}

	isProp = None
	propVar = None
	print("Prep: ", word.lemma_)
	
	for dep in findDependencies(word):
		print("Dependency equals: ", dep.dep_)
		if dep.dep_ == "pobj":
			if word.lemma_ == "of":
				var2 = gn.generateName()
				var3 = gn.generateName()
				res = parseNoun(dep, var3, prop)
				varToBeShown += res["varToBeShown"]
				statement += res["statement"]
				replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
				isProp = True
				propVar = var3
			elif word.lemma_ == "as":
				return {'property': dep}
			else:
				raise ValueError
		elif dep.dep_ == "":
			pass
		else:
			raise ValueError
	
	
	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary, "isProp": isProp, "propVar": propVar}

def parseDet(word, var):
	varToBeShown = []
	statement = ""
	replaceDictionary = {}

	if word.lemma_ in questionWords:
		varToBeShown.append(var)
	
	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}

def findDep(word, dependency):
	for dep in findDependencies(word):
		if dep.dep_ == dependency:
			return dep
	return None

def createCombinations(word):
	combinations = []
	
	i = word.i
	while i >= 0 and word.doc[i] in word.subtree:
		j = word.i

		if word.doc[i].dep_ == "det":
			#print(word.doc[i] + " " + word.doc[i].dep_)
			isOkay1 = False
		else:
			isOkay1 = True
		while isOkay1 and j < len(word.doc) and word.doc[j] in word.subtree:
			string = ""
			isOkay = True

			for k in range(i,j + 1):
				if word.doc[k].dep_ == "prep":
					w = findDep(word.doc[k], "pobj")
					print(w)
					if (w.i in range(i,j + 1)) == False:
						isOkay = False
				if k == j:
					string += word.doc[k].lemma_
				else:
					string += word.doc[k].text_with_ws
			string = string.rstrip()
			start = i
			length = j - i + 1
			combination = {"string": string, "start": start, "length": length}
			if (combination in combinations) == False and isOkay:
				combinations.append(combination)
				print(combination)
			j += 1
		i -= 1
	print("Combination:")
	print(combinations)
	print("\n")
	return combinations

def generateStatements(word, combination, var, prop):
	print("Noun: " + word.text)
	print(combination["string"])
	sentence = word.doc.text
	print(sentence)
	sentence = sentence.replace(combination["string"], "part")
	print(sentence)
	rel = nlp(sentence)
	w = rel[combination["start"]]
	string = combination["string"]

	
	varToBeShown = []
	statement = ""
	replaceDictionary = {}

	isProp = None

	for dep in findDependencies(w):
		print("Current dependency for " + string + ": " + dep.dep_)
		if dep.dep_ == "prep":
			if dep.i <= w.i:
				i = dep.i
			else:
				i = dep.i + combination["length"] - 1
			res = parsePrep(word.doc[i], var, prop)
			
			varToBeShown += res["varToBeShown"]
			statement += res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			
			if isProp == None:
				isProp = res["isProp"] #TODO: Check this for efficiency and properness
				propVar = res["propVar"]
			elif isProp != res["isProp"]:
				raise ValueError
		elif dep.dep_ == "det":
			res = parseDet(dep, var)
			varToBeShown += res["varToBeShown"]
			statement += res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		elif dep.dep_ == "acl":
			pass
		else:
			raise ValueError

	print("\n\n\n\n\n _______\n" + string.lower() +" \n" + str(questionWords))
	if string.lower() in questionWords:
		selectVar = createSelectName(combination["start"])
		statement += "BIND(" + var + " AS " + selectVar + ").\n"
		#replaceDictionary[var] = selectVar
		varToBeShown.append(selectVar)
		return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}
	if prop != None:
		isProp = True
		propVar = prop
	property = None
	if isProp == True:
		if string in countWords:
			#implement that it shows the count for the propVar
			varToBeShown.append(propVar)
		else:
			#if find(string + " of", True) != []:
			#	string = string + " of"
			#	rvar = createName(string, True)
			#	replaceDictionary[rvar] = ("wdt:", find(string, True))
			#	statement += var + " " + rvar + " " + propVar
			#else:
			union = False
			if find(string, True) != []:
				rvar = createName(string, True)
				replaceDictionary[rvar] = ("wdt:", find(string, True))
				statement += "{"+propVar + " " + rvar + " " + var+"}"
				union = True
			if find(string + " of", True) != []:
				if union:
					statement += " UNION "
				rvar = createName(string + " of", True)
				replaceDictionary[rvar] = ("wdt:", find(string + " of", True))
				statement += "{"+var + " " + rvar + " " + propVar + "}"

			if find(string + " of", True) == [] and find(string, True) == []:
				raise ValueError
			#rvar = createName(string, True)
			#replaceDictionary[rvar] = ("wdt:", find(string, True))
			#statement += propVar + " " + rvar + " " + var
			#if find(string, True) == []:
			#	raise ValueError
			property = string

	elif find(string, False) != []:
		rvar = createName(string, False)
		replaceDictionary[rvar] = ("wd:", find(string, False))
		statement += "{ \n"
		statement += "BIND("+rvar+" AS "+var+"). \n"
		statement += "} UNION { \n"
		statement += var+" wdt:P31 "+rvar+". \n"
		statement += "}\n"
	else:
		rvar = createName(string, True)
		uvar = gn.generateName()
		replaceDictionary[rvar] = ("wdt:", find(string, True))
		statement += uvar + " " + rvar + " " + var
		if find(string, True) == []:
			raise ValueError

	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary, "property": property}


def parseNoun(word, var, prop):
	varToBeShown = []
	statement = ""
	replaceDictionary = {}

	combinations = createCombinations(word)

	i = 0
	j = 0
	properties = []
	for combination in combinations:
		try:		
			print("Combination it is trying: "+str(combination) + "\n")
			res = generateStatements(word, combination, var, prop)
			varToBeShown += res["varToBeShown"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			if "property" in res and res["property"] != None:
				properties.append(res["property"])
			if res["statement"] != "":
				print("Included\n")
				if i > 0:
					statement += " UNION "
				statement += "{" + res["statement"] + "}\n"
				i += 1
			else:
				j = 1
		except ValueError:
			traceback.print_exc()

	if i + j == 0:
		raise ValueError

	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary, 'properties': properties}
