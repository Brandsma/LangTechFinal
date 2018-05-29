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

from Question_Classifier import classifyQuestion
from spacyFunctions import *
from sparqlFunctions import *

# switch = {
# 	whichQuestion: whichQuestionFunction,
# 	listQuestion: listQuestionFunction
# }
def main():
	# Load Spacy
	nlp = loadSpacyModel()

	# Input
	sen = input("Question: ")
	# Parse sentence
	doc = nlp(sen)

	# Question Classifier
	QuestionType = classifyQuestion(sen, nlp)
	# Switch based on question type
		# Function for each question
		# Each question returns an answer
	print(QuestionType)
	# answer = switch[QuestionType](question)
	# print answer

if __name__ == "__main__":
	main()
