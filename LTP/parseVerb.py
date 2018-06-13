import spacy

from dependency import *
from parseNoun import *
from generateName import *

printVerbs = ["show", "print", "describe", "name", "display", "list", "demonstrate", "illustrate", "showcase", "publish", "unveil", "exhibit", "disclose", "present", "tell", "give", "say", "return", "report", "state"]
inProperties = ["country", "continent", "city"]
properties = {"big": "P2046", "small": "P2046", "large": "P2046", "high": "P2044", "low": "P2044"}
def findSubjectObjectRelation(word, verb, dobj, nsubjv, dobjv):
	statement = ""
	varToBeShown = []
	replaceDictionary = {}

	pvar = createName(verb, True)
	propertyIds = find(verb, True)
	
	statement1 = ""
	try:
		statement1 = "{\n"
		res = parseNoun(dobj, dobjv, nsubjv)
		statement1 += res['statement']
		varToBeShown += res['varToBeShown']
		replaceDictionary = concatDict(replaceDictionary, res['replaceDictionary'])
		statement1 += "}\n"
	except ValueError:
		statement1 = ""
	
	statement2 = ""
	if propertyIds != []:
		replaceDictionary[pvar] = ("wdt:",propertyIds)
		try:
			res = parseNoun(dobj, dobjv, None)
			varToBeShown += res['varToBeShown']
			replaceDictionary = concatDict(replaceDictionary, res['replaceDictionary'])
			statement2 += "{\n"			
			statement2 += res['statement']
			statement2 += nsubjv + " " + pvar + " " + dobjv + ".\n"
			statement2 += "}"
			statement2 += " UNION {\n"
			statement2 += res['statement']
			statement2 += dobjv + " " + pvar + " " + nsubjv + ".\n"
			statement2 += "}\n"
		except ValueError:
			statement2 = ""

	if statement1 != "":
		statement1 += " UNION " + statement2
	else:
		statement1 = statement2
	if statement1 == "":
		raise ValueError
	else:
		statement += statement1
	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}

def parsePrepVerb(p, var):
	statement = ""
	varToBeShown = []
	replaceDictionary = {}
	pobj = findDep(p, "pobj")
	if pobj == None:
		pobj = findDep(p, "pcomp")
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

def createString(subtree):
	string = ""
	for s in subtree:
		string += s.text + " "
	string.rstrip()
	return string

def parseAmodAcomp(word, var):
	advmod = findDep(word, "advmod")
	statement = ""
	varToBeShown = []
	replaceDictionary = {}

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

def parseVerb(word, var):
	varToBeShown = []
	statement = ""
	replaceDictionary = {}

	verbString = word.lemma_
	isDisplayCommand = False

	#subj = gn.generateName()
	#obj = gn.generateName()

	#attr = gn.generateName()
	#prep = gn.generateName()

	nsubj = []
	dobj = []
	attr = []
	prep = []
	prop = []
	ccomp = []
	advmod = []
	relcl = []
	amod = []

	highestProperties = []

	isRoot = False
	for dep in findDependencies(word):
			if dep.dep_ == "nsubj" or dep.dep_ == "nsubjpass":
				nsubj.append(dep)
			elif dep.dep_ == "dobj":
				dobj.append(dep)
			elif dep.dep_ == "attr":
				attr.append(dep)
			elif dep.dep_ == "prep":
				if dep.lemma_ == "of":
					#verbString += " of"
					dobj.append(findDep(dep, "pobj"))
				elif dep.lemma_ == "as":
					prop.append(findDep(dep, "pobj"))
				else:
					prep.append(dep)
			elif dep.dep_ == "ROOT":
				isRoot = True
				pass
			elif dep.dep_ == "punct":
				pass
			elif dep.dep_ == "ccomp" :
				ccomp.append(dep)
			elif dep.dep_ == "advmod":
				advmod.append(dep)
			elif dep.dep_ == "aux" or dep.dep_ == "auxpass":
				pass
			elif dep.dep_ == "relcl":
				relcl.append(dep)
			elif dep.dep_ == "amod" or dep.dep_ == "acomp":
				amod.append(dep)
			else:
				raise ValueError

	nsubjv = gn.generateName()
	dobjv = gn.generateName()

	if len(ccomp) > 0:
		return parseVerb(ccomp[0], var)

	if len(nsubj) == 0 and len(dobj) > 0:
		predominantEntity = dobjv
	else:
		predominantEntity = nsubjv

	for s in nsubj:
		res = parseNoun(s, nsubjv, None)
		statement += res['statement']
		varToBeShown += res['varToBeShown']
		replaceDictionary = concatDict(replaceDictionary, res['replaceDictionary'])
		
	for a in attr:
		res = parseNoun(a, predominantEntity, None)
		statement += res['statement']
		varToBeShown += res['varToBeShown']
		replaceDictionary = concatDict(replaceDictionary, res['replaceDictionary'])

	if len(dobj) > 0:
		if len(prop) > 0:
			res = parseNoun(dobj[0], dobjv, None)
			statement += res['statement']
			varToBeShown += res['varToBeShown']
			replaceDictionary = concatDict(replaceDictionary, res['replaceDictionary'])
			
			propVar = createName(createString(prop[0].subtree), True)
			replaceDictionary[propVar] = ("wdt:",find(createString(prop[0].subtree), True))
			highestProperties += propVar
			statement += nsubjv + " " + propVar + " " + dobjv + ".\n"
		elif isRoot and verbString in printVerbs:
			res = parseNoun(dobj[0], dobjv, None)
			statement += res['statement']
			varToBeShown += res['varToBeShown']
			replaceDictionary = concatDict(replaceDictionary, res['replaceDictionary'])
		elif len(relcl) == 0:
			res = findSubjectObjectRelation(word, verbString, dobj[0], nsubjv, dobjv)
			statement += res['statement']
			varToBeShown += res['varToBeShown']
			replaceDictionary = concatDict(replaceDictionary, res['replaceDictionary'])

	if isRoot and verbString in printVerbs:
		varToBeShown.append(dobjv)

	for p in prep:
		res = parsePrepVerb(p, nsubjv)
		statement += res['statement']
		varToBeShown += res['varToBeShown']
		replaceDictionary = concatDict(replaceDictionary, res['replaceDictionary'])

	for a in advmod:
		if a.lemma_ == "how":
			varToBeShown.append(nsubjv) # is this correct?

	for a in amod:
		res = parseAmodAcomp(a, nsubjv)
		statement += res['statement']
		varToBeShown += res['varToBeShown']
		replaceDictionary = concatDict(replaceDictionary, res['replaceDictionary'])

	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}
	
