import sys
import requests
import spacy
from SPARQLWrapper import SPARQLWrapper, JSON
from language_parser import *
from sparql_req import *
from language_parser import *

#
# Run this file
#

# Required Libraries
# 	- Spacy
# 	- SPARQLWrapper

# Download:
# sudo pip3 install -u spacy
# sudo pip3 install SPARQLWrapper

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
	return nounObject

def findPropNoun(nounObject):
	prop_noun = ""
	for child in nounObject.children:
		if child.dep_ == 'prep':
			for kid in child.children:
				if kid.dep_ == 'pobj':
					for peewee in kid.children:
						if peewee.dep_ == 'compound':
							# Append a compound if applicable
							prop_noun = peewee.text
					# This is our concept 
					if prop_noun == "":
						prop_noun = kid.text
					else:
						prop_noun = prop_noun + " " + kid.text
	return prop_noun

def handleQuestion(question):
	# Load language model
	nlp = spacy.load('en')
	# Annotate question with linguistic data
	doc = nlp(question)

	# Find the dependency with the highest precedence for our sentences
	nounObject = findHighestPrecedenceDependency(doc)

	# This is our property
	noun = nounObject.text

	# This is our concept
	prop_noun = findPropNoun(nounObject)
	
	# Check if we actually found something
	if noun == "" or prop_noun == "":
		print("Failed to parse the question")
		return

	# Create and fire the query
	wdNoun = getWikidataConcept(prop_noun)['id']
	wdtNoun = getWikidataProperty(noun)['id']

	query = createQuery(wdNoun, wdtNoun)
	try:
		print("\t" + fireQuery(query)['results']['bindings'][0]['targetLabel']['value'])
	except IndexError:
		print("I could not find an answer")

# Main function
def main():
	# Dict with all the questions
	questions = { 'Q1' : "When was the inception of Serbia?",
			  'Q2' : "The anthem of Germany, what is it?",
			  'Q3' : "the capital of Azerbaijan, what is it?",
			  'Q4' : "Give me the capital of Serbia",
			  'Q5' : "Tell me the birthdate of John Lennon",
			  'Q6' : "What is the motto of South Africa?",
			  'Q7' : "Tell me the population of Greenland?",
			  'Q8' : "Tell me the timezone of Syria?",
			  'Q9' : "The population of Germany, what is it?",
			  'Q10' : "Who is the president of France?",
			  'Q11' : "Who is the queen of United Kingdom?" }	
	# for label in questions:
	# 	# Prints from a dict, so arbitrary order
	# 	print(label + ": " + questions[label])	 
	# print(" ") 
	# for label in questions:
	# 	print("Question: " + questions[label])
	# 	handleQuestion(questions[label])
	handleQuestion(input("Question: "))
	# inp = input("Question: ")
	# while(inp != '!'):
	# 	handleQuestion(inp)
	# 	inp = input("Question: ")
	# displayEntity(questions['Q4'])

if __name__ == "__main__":
	main()