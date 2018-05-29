# Find the Root
# Look at Dependencies of Root
# Find {'nsubj', 'dobj', 'prep', 'attr', 'ccomp'} (Question words can also be attributes)
# With those dependencies find the subject and object
# What's type of the question
	#Does root have a nsubj:
		# NO: 
			# list/show/print/ hwatadffaheve
		# YES:
			# iS 'is' the root the first word in the snetences?
				#YES: yes/no
				#NO:
					# Do you find "how many" "how much"
						# YES:
							#Count question
						# NO:
							# Do you find "which" "who" "what" "How" etc.
								#YES:
									#Which question
								#NO:
									# Did you find the dep acomp("How big is china?")
										#YES:
											# How big question (How far above sea level)
										#NO:
											# Handle Special cases (could you give me the population of the Netherlands?)
											# Otherwise raise error
from enum import Enum
class QuestionTypes(Enum):
	whichQuestion = 1
	countQuestion = 2
	listQuestion = 3
	YesNoQuestion = 4
	HowBigQuestion = 5

def isCountQuestion(question):
	return question.find("how many") != -1 or question.find("how much") != -1

def isWhichQuestion(question):
	return question.find("which") != -1 or question.find("who") != -1 or question.find("what") != -1 or question.find("how") != -1

def findRoot(doc):
	for token in doc:
		if token.dep_ == 'ROOT':
			return token
def hasDependency(token, dep):
	for child in token.children:
		if child.dep_ == dep:
			return True
	return False

def classifyQuestion(question, nlp):
	parsedQuestion = nlp(question)
	root = findRoot(parsedQuestion)
	if not hasDependency(root, "nsubj"):
		return QuestionTypes.listQuestion
	elif root == parsedQuestion[0]:
		return QuestionTypes.YesNoQuestion
	elif isCountQuestion(question):
		return QuestionTypes.countQuestion
	elif isWhichQuestion(question):
		return QuestionTypes.whichQuestion
	elif hasDependency(root, "acomp"):
		return QuestionTypes.HowBigQuestion
	else:
		raise ValueError
		