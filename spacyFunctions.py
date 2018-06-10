import spacy

def loadSpacyModel():
	return spacy.load('en')

def displayDependency(doc, nlp):
	spacy.displacy.serve(doc, style='dep')