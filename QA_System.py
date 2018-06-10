from spacyFunctions import *
from sparqlFunctions import *

def whichQuestionParser(question, nlp):
	doc = nlp(question)
	return "Very nice which question"

def listQuestionParser(question, nlp):
	doc = nlp(question)
	return "Very nice list question"

def YesNoQuestionParser(question, nlp):
	doc = nlp(question)
	return "Very nice Yes/No question"

def HowBigQuestionParser(question, nlp):
	doc = nlp(question)
	return "Very nice How Big question"


def findHighestPrecedenceDependency(doc):
	nounDep = ""
	wh_lemma = ""
	for token in doc:
		# Find the question word
		# What - Who - Where - When - Why - How - ...?
		if token.tag_ == 'WP' or token.tag_ == 'WDT' or token.tag_ == 'WP$' or token.tag_ == 'WRB':
			wh_lemma = token.lemma_
		# Find the root of the parse tree
		if token.dep_ == 'ROOT':
			root_token = token
		# From the root we can find all info we need for a full question parse
	for child in root_token.children:
		if child.dep_ == 'dep':
			nounObject = child
			nounDep = 'dep'
			break
		if child.dep_ == 'dobj':
			if nounDep != 'dep':
				nounObject = child
				nounDep = 'dobj'
		if child.dep_ == 'nsubj':
			if nounDep != 'dep' and nounDep != 'dobj':
				nounObject = child
				nounDep = 'nsubj'
		if child.dep_ == 'attr' and child.lemma_ != wh_lemma:
			if nounDep != 'dep'  and nounDep != 'dobj' and nounDep != 'nsubj':
				nounObject = child
				nounDep = 'attr'
	return [nounObject, root_token]

def expandWord(word, doc):
	wordString = ""
	expectedWords = getExpectedWords(word)
	expectedWords.append(word)
	for token in doc:
		if token in expectedWords:
			wordString = wordString + " " + token.text
	return wordString

def getExpectedWords(word):
	expectedWords = []
	for child in word.children:
		if child.text == "many" or child.text == "much":
			continue
		expectedWords.append(child)
	for token in expectedWords:
		if token.dep_ == "prep":
			expectedWords.append(getExpectedWords(token)[0])
	return expectedWords

def findSentenceProperty(root, doc):
	senProperty = ""
	for child in root.children:
		if child.dep_ == 'nsubj':
			senProperty = expandWord(child, doc)
			break
	try:
		# If the found property is not a property use the root verb
		wdt = getWikidataProperty(senProperty)
	except:
		senProperty = root.text
		wdt = getWikidataProperty(senProperty)
	return senProperty

def constructCountQuery(prop, concept):
	query = ("SELECT " + "(COUNT(*) as ?target) " + "\n" +
			"WHERE { " + "wd:" + concept + " wdt:" + prop + " ?target" + "\n" +
			" }" + " LIMIT 1")
	return query

def countQuestionParser(question, nlp):
	#TODO: expand capabilities, is now capable of (How many countries border X?)
	doc = nlp(question)
	# Find Root of question
	# Find nsubj, if nsubj is property-less noun, check root for property
	[senSubject, rootObject] = findHighestPrecedenceDependency(doc)
	senProperty = findSentenceProperty(rootObject, doc)

	senSubject = expandWord(senSubject, doc)

	try:
		wd = getWikidataConcept(senSubject)['id']
		wdt = getWikidataProperty(senProperty)['id']
	except IndexError:
		print("Failed to find either the concept or the property") 

	query = constructCountQuery(wdt, wd)

	try:
		print("\t" + fireQuery(query)['results']['bindings'][0]['target']['value'])
	except IndexError:
		print("I could not find an answer")
	#displayDependency(doc, nlp)
	return "Very nice count question"

question = ["How many countries border the united states of the america?"]
#, "How many citizens does Africa have?", "How many people live in Serbia?",
# "How many citizens does Africa have?", 
# "How many countries border Paraguay?"]

nlp = loadSpacyModel()
for q in question:
	print("Question: " + q)
	countQuestionParser(q, nlp)