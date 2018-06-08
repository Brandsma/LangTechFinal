import spacy

def loadSpacyModel():
	return spacy.load('en')

def displayDependency(sen, nlp):
	doc = nlp(sen)
	spacy.displacy.serve(doc, style='dep')