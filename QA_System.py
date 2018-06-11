from spacyFunctions import *
from sparqlFunctions import *
from nltk.corpus import wordnet as wn
import sys

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
		if child.dep_ == 'prep':
			for c in child.children:
				if c.dep_ == 'pobj':
					nounObject = c
					nounDep = 'prep'
			break
		if child.dep_ == 'dep':
			if nounDep != 'prep':
				nounObject = child
				nounDep = 'dep'	
		if child.dep_ == 'dobj':
			if nounDep != 'dep' and nounDep != 'prep':
				nounObject = child
				nounDep = 'dobj'
		if child.dep_ == 'nsubj':
			if nounDep != 'dep' and nounDep != 'dobj' and nounDep != 'prep':
				nounObject = child
				nounDep = 'nsubj'
		if child.dep_ == 'attr' and child.lemma_ != wh_lemma:
			if nounDep != 'dep'  and nounDep != 'dobj' and nounDep != 'nsubj' and nounDep != 'prep':
				nounObject = child
				nounDep = 'attr'
	return [nounObject, root_token]

def expandWord(word, doc):
	wordString = ""
	expectedWords = getExpectedWords(word)
	expectedWords.append(word)
	for token in doc:
		if token in expectedWords:
			if wordString == "":
				wordString = token.text
			else:
				wordString = wordString + " " + token.text
	return wordString

def getExpectedWords(word):
	expectedWords = []
	for child in word.children:
		if child.text == "many" or child.text == "much":
			continue
		expectedWords.append(child)
	for token in expectedWords:
		try:
			if token.dep_ == "prep":
				expectedWords.append(getExpectedWords(token)[0])
			elif token.dep_ == "compound":
				expectedWords.append(getExpectedWords(token)[0])
		except IndexError:
			pass
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
	if root.lemma_ == "border":
		senProperty = "border"
	return senProperty

def constructCountQuery(senProperty, senSubject):
	# Return a query that counts the number of columns
	try:
		concept = getWikidataConcept(senSubject)['id']
		prop = getWikidataProperty(senProperty)['id']
	except IndexError:
		return ""
	query = ("SELECT " + "(COUNT(*) as ?target) " + "\n" +
			"WHERE { " + "wd:" + concept + " wdt:" + prop + " ?target" + "\n" +
			" }")
	return query

def constructNumberQuery(senProperty, senSubject):
	# Return a query that gets the answer from the column
	try:
		concept = getWikidataConcept(senSubject)['id']
		prop = getWikidataProperty(senProperty)['id']
	except IndexError:
		return ""
	query = ("SELECT " + "?target " + "\n" +
			"WHERE { " + "wd:" + concept + " wdt:" + prop + " ?target" + "\n" +
			" }")
	return query

def tryQuery(query):
	try: 
		return fireQuery(query)['results']['bindings'][0]['target']['value']
	except IndexError:
		return 0

def lemmalist(s):
	# Find synonyms of a word so that wikidata queries have more chance
	syn_set = []
	i = 0
	try:
		for lemma in wn.synsets(s)[0].lemmas():
			syn_set.append(lemma.name())
			i = i + 1
			if i == 4:
				# We do not want _too_ many options
				break;
	except IndexError:
		return [s]
	return syn_set

def findMostLikelyAnswer(answers):
	# The likeliest answer is usually the highest number in the answers array
	# Better heuristics can probably be used, but it works most of the time
	MostLikelyAnswer = 0
	for answer in answers:
		try:
			tempAnswer = float(answer)
		except ValueError:
			continue
		if tempAnswer > MostLikelyAnswer:
			MostLikelyAnswer = tempAnswer
	return MostLikelyAnswer

def lexicalVariationSolver(senProperty, senSubject):
	# This fixes the problems where the synonyms from nltk do not work
	# Population case
	if senProperty == "citizens" or senProperty == "people":
		senProperty = "population"
	if senSubject == "citizens" or senSubject == "people":
		senSubject = "population"
	return [senSubject, senProperty]

def countQuestionParser(question, nlp):
	print("Trying to find an answer to the count question...")
	print("This may take a minute")
	answer = [0] * 65
	query = [""] * 65

	doc = nlp(question)

	[senSubject, rootObject] = findHighestPrecedenceDependency(doc)
	senProperty = findSentenceProperty(rootObject, doc)

	senSubject = expandWord(senSubject, doc)

	[senSubject, senProperty] = lexicalVariationSolver(senProperty, senSubject)

	possibleSubjects = lemmalist(senSubject)
	possibleProperties = lemmalist(senProperty)

	i = 0
	for subject in possibleSubjects:
		for property in possibleProperties:
			query[i] = constructCountQuery(senProperty, senSubject)
			query[i+15] = constructCountQuery(senSubject, senProperty) 
			query[i+31] = constructNumberQuery(senProperty, senSubject)
			query[i+47] = constructNumberQuery(senSubject, senProperty)
			i = i + 1

	i = 0
	for q in query:
		if q != "":
			answer[i] = tryQuery(q)
		i = i + 1

	return findMostLikelyAnswer(answer)