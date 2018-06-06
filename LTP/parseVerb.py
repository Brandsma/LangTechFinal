import spacy

from dependency import *
from parseNoun import *
from generateName import *

printVerbs = ["show", "print", "describe", "name", "display", "list", "demonstrate", "illustrate", "showcase", "publish", "unveil", "exhibit", "disclose", "present"]

def parseVerb(word, var):
	varToBeShown = []
	statement = ""
	replaceDictionary = {}

	isDisplayCommand = False

	subj = gn.generateName()
	obj = gn.generateName()

	attr = gn.generateName()
	prep = gn.generateName()

	for dep in findDependencies(word):
		if dep.dep_ == "nsubj":
			res = parseNoun(dep, subj)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		elif dep.dep_ == "dobj":
			res = parseNoun(dep, obj)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		elif dep.dep_ == "attr":
			res = parseNoun(dep, attr)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		elif dep.dep_ == "prep":
			res = parsePrep(dep, attr)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			if dep.text == "of":
				raise ValueError
		elif dep.dep_ == "ROOT":
			if word.lemma_ in printVerbs and hasDependency(word, "nsubj") == False:
				varToBeShown.append(obj)
				isDisplayCommand = True
			elif hasDependency(word, "nsubj") == False:
				raise ValueError
		elif dep.dep_ == "punct":
			pass
		else:
			raise ValueError

	if isDisplayCommand == False and hasDependency(word, "nsubj") == False:
		raise ValueError
	
	if isDisplayCommand:
		replaceDictionary[attr] = ("", obj)
		replaceDictionary[prep] = ("", obj)
	else:
		replaceDictionary[attr] = ("", subj) # I'm not sure if this is right
		replaceDictionary[prep] = ("", subj)

	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}
