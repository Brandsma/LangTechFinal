import spacy

from dependency import *
from parseNoun import *
from generateName import *

printVerbs = ["show", "print", "describe", "name", "display", "list", "demonstrate", "illustrate", "showcase", "publish", "unveil", "exhibit", "disclose", "present", "tell", "give", "say", "return", "report"]

def parseVerb(word, var):
	varToBeShown = []
	statement = ""
	replaceDictionary = {}

	isDisplayCommand = False

	subj = gn.generateName()
	obj = gn.generateName()

	attr = gn.generateName()
	prep = gn.generateName()

	if hasDependency(word, "ROOT"):
		isRoot = True
	else:
		isRoot = False
	#what happens if it is a print command.
	if hasDependency(word, "nsubj") == False and hasDependency(word, "nsubjpass") == False and word.lemma_ in printVerbs:
		if hasDependency(word, "relcl") or hasDependency(word, "ccomp"):
			if hasDependency(word, "relcl"):
				res = parseVerb(findDep(word,"relcl"), None)
			else:
				res = parseVerb(findDep(word,"ccomp"), None)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])	
		elif hasDependency(word, "dobj"):
			res = parseNoun(findDep(word,"dobj"), obj, None)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			varToBeShown.append(obj)
			isDisplayCommand = True
		else:
			raise ValueError
		return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}	
	else:
		isRoot = False

	#what should happen if it is an is sentence
	if word.lemma_ == "be":
		for dep in findDependencies(word):
			if dep.dep_ == "nsubj":
				res = parseNoun(dep, subj, None)
				varToBeShown += res["varToBeShown"]
				statement +=  res["statement"]
				replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			elif dep.dep_ == "dobj":
				res = parseNoun(dep, obj, None)
				varToBeShown += res["varToBeShown"]
				statement +=  res["statement"]
				replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			elif dep.dep_ == "attr":
				res = parseNoun(dep, attr, None)
				varToBeShown += res["varToBeShown"]
				statement +=  res["statement"]
				replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			elif dep.dep_ == "prep":
				res = parsePrep(dep, attr, None)
				varToBeShown += res["varToBeShown"]
				statement +=  res["statement"]
				replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
				if dep.text == "of":
					raise ValueError
			elif dep.dep_ == "ROOT":
				pass
				#print("WORD: " + str(word))
				#if word.lemma_ in printVerbs and hasDependency(word, "nsubj") == False:
				#	varToBeShown.append(obj)
				#	isDisplayCommand = True
				#elif hasDependency(word, "nsubj") == False:
				#	raise ValueError
			elif dep.dep_ == "punct":
				pass
			elif dep.dep_ == "ccomp" : 
				res = parseVer(dep, None)
				varToBeShown += res["varToBeShown"]
				statement +=  res["statement"]
				replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			elif dep.dep_ == "advmod":
				advmod = dep
			else:
				raise ValueError

		#if isDisplayCommand == False and hasDependency(word, "nsubj") == False:
		#	raise ValueError
		
		if isDisplayCommand:
			replaceDictionary[attr] = ("", obj)
			replaceDictionary[prep] = ("", obj)
		else:
			print("Hello " + attr + " " + subj)
			replaceDictionary[attr] = ("", subj) # I'm not sure if this is right
			replaceDictionary[prep] = ("", subj)

		if advmod.lemma_ == "how":
			svar = createSelectName(dep.i)
			statement += "BIND(" + subj + " as " + svar + ").\n"
			varToBeShown.append(svar)

		return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}
	#what should happen if it is an have sentence
	if word.lemma_ == "have":
		#find property
		dobj = None
		property = None
		for dep in findDependencies(word):
			print("DEPENDENCY:  " + dep.dep_)
			if dep.dep_ == "nsubj":
				res = parseNoun(dep, subj, None)
				varToBeShown += res["varToBeShown"]
				statement +=  res["statement"]
				replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			elif dep.dep_ == "dobj":
				if dobj == None:
					dobj = dep
				else:
					raise ValueError
			elif dep.dep_ == "attr":
				res = parseNoun(dep, attr, None)
				varToBeShown += res["varToBeShown"]
				statement +=  res["statement"]
				replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			elif dep.dep_ == "prep":
				res = parsePrep(dep, attr, None)
				if 'property' in res:
					if res["property"] != None:
						if property == None:
							property = res["property"]
						else:
							raise ValueError
				else:
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
			elif dep.dep_ == "ccomp" : 
				res = parseVer(dep, None)
				varToBeShown += res["varToBeShown"]
				statement +=  res["statement"]
				replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			elif dep.dep_ == "aux":
				pass
			else:
				raise ValueError
		if property != None:
			res = parseNoun(dobj, obj, None)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
			res = parseNoun(property, obj, subj)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		else:
			res = parseNoun(dobj, obj, subj)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])

		return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}
	#what should happen if it is another verb

	dobj = None
	property = None
	for dep in findDependencies(word):
		print("DEPENDENCY:  " + dep.dep_)
		if dep.dep_ == "nsubj" or dep.dep_ == "nsubjpass":
			res = parseNoun(dep, subj, None)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		elif dep.dep_ == "dobj":
			if dobj == None:
				dobj = dep
			else:
				raise ValueError
		elif dep.dep_ == "attr":
			res = parseNoun(dep, attr, None)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		elif dep.dep_ == "prep":
			res = parsePrep(dep, attr, None)
			if 'property' in res:
				if res["property"] != None:
					if property == None:
						property = res["property"]
					else:
						raise ValueError
			else:
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
		elif dep.dep_ == "ccomp" : 
			res = parseVer(dep, None)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		elif dep.dep_ == "aux" or dep.dep_ == "auxpass":
			pass
		elif dep.dep_ == "advmod":
			advmod = dep
			
		else:
			raise ValueError
	if property != None:
		raise ValueError
	else:
		if dobj != None:
			res = parseNoun(dobj, obj, None)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		pvar = createName(word.lemma_, True)
		propertyIds = find(word.lemma_, True)
		if propertyIds != []:
			replaceDictionary[pvar] = propertyIds
		else:
			raise ValueError
		statement += subj + " " + pvar + " " + obj + ".\n"

		if dep.lemma_ == "how":
				svar = createSelectName(dep.i)
				statement += "BIND(" + obj + " as " + svar + ").\n"
				varToBeShown.append(svar)
		#	elif dep.lemma_ == "when":
		#		pass
		#	elif dep.lemma_ == "where":
		#		if (property in locationWords) == False:
		#			statement += 
		#		pass
		#	else:
		#		raise ValueError

	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}
	#-------------
	#if word.lemma_ == "have":
		#look for property.
		#if hasDependency(word, "prep") and getDep(word, "prep"):


	for dep in findDependencies(word):
		if dep.dep_ == "nsubj":
			res = parseNoun(dep, subj, None)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		elif dep.dep_ == "dobj":
			res = parseNoun(dep, obj, None)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		elif dep.dep_ == "attr":
			res = parseNoun(dep, attr, None)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])
		elif dep.dep_ == "prep":
			res = parsePrep(dep, attr, None)
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
		elif dep.dep_ == "ccomp" : 
			res = parseVer(dep, None)
			varToBeShown += res["varToBeShown"]
			statement +=  res["statement"]
			replaceDictionary = concatDict(replaceDictionary, res["replaceDictionary"])	
		else:
			raise ValueError

	if isDisplayCommand == False and hasDependency(word, "nsubj") == False:
		raise ValueError
	
	if isDisplayCommand:
		replaceDictionary[attr] = ("", obj)
		replaceDictionary[prep] = ("", obj)
	else:
		print("Hello " + attr + " " + subj)
		replaceDictionary[attr] = ("", subj) # I'm not sure if this is right
		replaceDictionary[prep] = ("", subj)

	return {"varToBeShown": varToBeShown, "statement": statement, "replaceDictionary": replaceDictionary}
