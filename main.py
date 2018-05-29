# Types of questions
# Pattern match on the dependecies

# Function to solve What is X of Y question
# Find the root
# Verb


# 			Question classifier
# Find the dependecies of Root
# { 'nsubj', 'attr', 'dobj', 'dep', ,'prep', 'pobj', 'compound' }



# What/Who is/are the X of Y
# List-questions
# Yes/No Questions
# Count questions
# (Highest/Deepest Questions)
# (Questions with qualified statements)

# 			Function for each type of question

# 			Query Creator

# 			Query Fire

#
# Deadline: 6th of June
#

from Question_Classifier import classifyQuestion, QuestionTypes
from spacyFunctions import *
from sparqlFunctions import *
from QA_System import *

def main():
	questionParseDict = {
		QuestionTypes.whichQuestion : whichQuestionParser,
		QuestionTypes.countQuestion : countQuestionParser,
		QuestionTypes.listQuestion : listQuestionParser,
		QuestionTypes.YesNoQuestion : YesNoQuestionParser,
		QuestionTypes.HowBigQuestion : HowBigQuestionParser
	}
	# Load Spacy
	print("Please wait for the Spacy model to load...")
	nlp = loadSpacyModel()

	# Input
	sen = ""
	while sen == "":
		sen = input("Question: ")
	# Parse sentence
	doc = nlp(sen)

	# Question Classifier
	QuestionType = classifyQuestion(sen, doc)
	# Switch based on question type
		# Function for each question
		# Each question returns an answer
	answer = questionParseDict[QuestionType](sen, nlp)
	print(answer) 

if __name__ == "__main__":
	main()
