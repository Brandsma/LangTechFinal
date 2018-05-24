import spacy

def displayDependency(sen):
	nlp = spacy.load('en')
	doc = nlp(sen)
	for token in doc:
		if token.dep_ == 'ROOT':
			print("Root: " + token.text)
	spacy.displacy.serve(doc, style='dep')

def displayEntity(sen):
	nlp = spacy.load('en')
	doc = nlp(sen)
	spacy.displacy.serve(doc, style='ent')

def tagSentence(sen):
	nlp = spacy.load('en')
	tagger = nlp.tagger(nlp.Vocab)
	doc = nlp(u"This is a sentence.")
	return tagger(doc)