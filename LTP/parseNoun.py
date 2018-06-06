import spacy
import traceback

from dependency import *
from find import *
from generateName import *

countWords = []

def parsePrep(word, var):
	rel = word.doc
	print("Prep: " + word.text)
	print("Sentence: " + rel.text)
	varToBeShown = []
	statement = ""
	replaceDictionary = {}

	isProp = None
	propVar = None
	print("Prep: ", word.lemma_)
	if word.lemma_ == "of":
		for dep in findDependencies(word):
			print("Dependency equals: ", dep.dep_)
			if dep.dep_ == "pobj":
				var2 = gn.generateName()
				var3 = gn.generateName()
				res = parseNoun(dep, var3)
				varToBeShown += res["varToBeShown"]
				statement += res["statement"]
				replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
				isProp = True
				propVar = var3
			elif dep.dep_ == "":
				pass
			else:
				raise ValueError
	else:
		raise ValueError
	
	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary, "isProp": isProp, "propVar": propVar}

def createCombinations(word):
	combinations = []
	
	combination = {"string": word.text, "start": word.i, "length": 1}
	combinations.append(combination)
	string = ""
	i = 0
	j = -1
	for w in word.subtree:
		string += w.text_with_ws
		i += 1
		if j == -1 or j > w.i:
			j = w.i
	string = string.rstrip()
	start = j
	length = i
	combination = {"string": string, "start": start, "length": length}
	combinations.append(combination)
	return combinations

def generateStatements(word, combination, var):
	print("Noun: " + word.text)
	print(combination["string"])
	sentence = word.doc.text
	print(sentence)
	sentence = sentence.replace(combination["string"], "word")
	print(sentence)
	rel = nlp(sentence)
	w = rel[combination["start"]]
	string = combination["string"]

	varToBeShown = []
	statement = ""
	replaceDictionary = {}

	isProp = None

	for dep in findDependencies(w):
		if dep.dep_ == "prep":
			if dep.i <= w.i:
				i = dep.i
			else:
				i = dep.i + combination["length"] - 1
			res = parsePrep(word.doc[i], var)
			
			varToBeShown += res["varToBeShown"]
			statement += res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			
			if isProp == None:
				isProp = res["isProp"] #TODO: Check this for efficiency and properness
				propVar = res["propVar"]
			elif isProp != res["isProp"]:
				raise ValueError
		elif dep.dep_ == "det":
			pass
		else:
			raise ValueError

	if string.lower() == "what":
		selectVar = createSelectName(combination["start"])
		#statement += "BIND(" + var + " AS " + selectVar + ").\n"
		replaceDictionary[var] = selectVar
		varToBeShown.append(selectVar)
		return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}

	if isProp == True:
		if string in countWords:
			#implement that it shows the count for the propVar
			varToBeShown.append(propVar)
		else:
			rvar = createName(string, True)
			replaceDictionary[rvar] = ("wdt:", find(string, True))
			statement += propVar + " " + rvar + " " + var
			if find(string, True) == []:
				raise ValueError

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

	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}


def parseNoun(word, var):
	varToBeShown = []
	statement = ""
	replaceDictionary = {}

	combinations = createCombinations(word)

	i = 0
	j = 0
	for combination in combinations:
		try:		
			res = generateStatements(word, combination, var)
			varToBeShown += res["varToBeShown"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])

			if res["statement"] != "":
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

	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}
