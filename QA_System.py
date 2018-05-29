def whichQuestionParser(question, nlp):
	doc = nlp(question)
	return "Very nice which question"

def listQuestionParser(question, nlp):
	doc = nlp(question)
	return "Very nice list question"

def countQuestionParser(question, nlp):
	doc = nlp(question)
	return "Very nice count question"

def YesNoQuestionParser(question, nlp):
	doc = nlp(question)
	return "Very nice Yes/No question"

def HowBigQuestionParser(question, nlp):
	doc = nlp(question)
	return "Very nice How Big question"