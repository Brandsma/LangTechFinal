import spacy
import traceback

from dependency import *
from find import *
from generateName import *

countWords = ["number", "count"]
questionWords = ["what", "who", "which", "how"]
inProperties = ["country", "continent", "city"]

def parseAmodAcomp(word, var):
	advmod = findDep(word, "advmod")
	statement = ""
	varToBeShown = []
	replaceDictionary = {}

	if advmod == None:
		raise ValueError

	if advmod.lemma_ == "how":
		if word.lemma_ == "many":
			varToBeShown.append("(count(distinct " + var + ") as ?item)")
		else:
			var1 = gn.generateName()
			adj = properties[word.lemma_]
			showVar = createSelectName(advmod.i)
			varToBeShown.append(showVar)
			statement += "OPTIONAL {" + var + " wdt:" + adj + " "+var1+"}"
			statement += "BIND(COALESCE(IF(isnumeric(" + var + "), " + var + ", 1/0), IF(BOUND(" + var1 + "), " + var1 + ", 1/0)) as "+showVar+")."
			statement += "FILTER(BOUND(" + showVar + "))"
	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}

def parsePrepVerb(p, var):
	statement = ""
	varToBeShown = []
	replaceDictionary = {}
	pobj = findDep(p, "pobj")
	if pobj == None:
		pobj = findDep(p, "pcomp")
	if pobj == None:
		return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}
	pobjv = gn.generateName()
	if pobj.pos_ != "NUM":
		res = parseNoun(pobj, pobjv, None)
		statement += res['statement']
		varToBeShown += res['varToBeShown']
		replaceDictionary = concatDict(replaceDictionary, res['replaceDictionary'])

		union = False
		for i in inProperties:
			prepVar = createName(i, True)
			replacements = find(i, True)
			if replacements != []:
				if union:
					statement += " UNION "
				statement += "{" + var + " " + prepVar + " " + pobjv + ".}"
				replaceDictionary[prepVar] = ("wdt:",replacements)
				union = True
	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}

def parsePrep(word, var, prop, string):
	rel = word.doc
	varToBeShown = []
	statement = ""
	replaceDictionary = {}

	isProp = None
	propVar = None
	
	if word.lemma_ == "of":
		for dep in findDependencies(word):
			if dep.dep_ == "pobj":
				if word.lemma_ == "as":
					return {'property': dep}
				else:	
					var2 = gn.generateName()
					var3 = gn.generateName()
					res = parseNoun(dep, var3, prop)
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
		replacements = find(string, True)

		if replacements == []:
			return parsePrepVerb(word, var)
		pobj = findDep(word, "pobj")
		var2 = gn.generateName()
		var3 = gn.generateName()
		res = parseNoun(pobj, var3, prop)
		varToBeShown += res["varToBeShown"]
		statement += res["statement"]
		replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		isProp = True
		propVar = var3
		
	#else:
	#	raise ValueError			
	
	
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
			isOkay1 = False
		else:
			isOkay1 = True
		while isOkay1 and j < len(word.doc) and word.doc[j] in word.subtree and (word.doc[j].dep_ == "prep" and word.doc[j].lemma_ != "of") == False:
			string = ""
			isOkay = True
			part = False
			for k in range(i,j + 1):
				if word.doc[k].lemma_ == "part":
					part = True
				if word.doc[k].dep_ == "prep":
					w = findDep(word.doc[k], "pobj")
					if (w.i in range(i,j + 1)) == False:
						isOkay = False
				if k == j:
					string += word.doc[k].lemma_
				else:
					string += word.doc[k].text_with_ws
			string = string.rstrip()
			start = i
			length = j - i + 1
			if word.pos_ == "PRON" or word.lemma_ in questionWords:
				replacement = word.text
			elif part:
				replacement = "word"
			else:
				replacement = "part"
			combination = {"string": string, "start": start, "length": length, "replacement": replacement}
			if (combination in combinations) == False and isOkay:
				combinations.append(combination)
			j += 1
		i -= 1
	return combinations

def generateStatements(word, combination, var, prop):
	sentence = word.doc.text
	sentence = sentence.replace(combination["string"], combination["replacement"])
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
			res = parsePrep(word.doc[i], var, prop, string)
			
			varToBeShown += res["varToBeShown"]
			statement += res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			
			if isProp == None:
				if "isProp" in res and "propVar" in res:
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
		elif dep.dep_ == "amod":
			if dep.lemma_ != "all" or dep.lemma_ != "current":
				res = parseAmodAcomp(dep, var)
				varToBeShown += res["varToBeShown"]
				statement += res["statement"]
				replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		else:
			raise ValueError


	if string.lower() in questionWords:
		selectVar = createSelectName(combination["start"])
		statement += "BIND(" + var + " AS " + selectVar + ").\n"
		#replaceDictionary[var] = selectVar
		varToBeShown.append(var)
		return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}
	if prop != None:
		isProp = True
		propVar = prop
	property = None
	if isProp == True:
		if string in countWords:
			statement1 = "SELECT (count(distinct " + propVar + ")  as " + var + ") WHERE {" + statement + "}\n"
			statement = statement1
		else:
			
			union = False
			cvar1 = gn.generateName()
			cvar2 = gn.generateName()
			coalesce = ""
			if find(string, True) != []:
				rvar = createName(string, True)
				replaceDictionary[rvar] = ("wdt:", find(string, True))
				statement += "OPTIONAL {"+propVar + " " + rvar + " " + cvar1+"}"
				coalesce += "IF(BOUND("+cvar1+"),"+cvar1+",1/0)"
				union = True
			if find(string + " of", True) != []:
				if union:
					coalesce += ", "
				coalesce += "IF(BOUND("+cvar2+"),"+cvar2+",1/0)"
				rvar = createName(string + " of", True)
				replaceDictionary[rvar] = ("wdt:", find(string + " of", True))
				statement += "OPTIONAL {"+cvar2 + " " + rvar + " " + propVar + "}"

			if find(string + " of", True) == [] and find(string, True) == []:
				raise ValueError

			statement += "BIND(COALESCE(" + coalesce + ") as " + var + ").\n"
		
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
			res = generateStatements(word, combination, var, prop)
			varToBeShown += res["varToBeShown"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			if "property" in res and res["property"] != None:
				properties.append(res["property"])
			if res["statement"] != "":
				if i > 0:
					statement += " UNION "
				statement += "{" + res["statement"] + "}\n"
				i += 1
			else:
				j = 1
		except ValueError:
			pass
			
	if i + j == 0:
		raise ValueError

	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary, 'properties': properties}
