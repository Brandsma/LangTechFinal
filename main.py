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

switch = {
	whichQuestion: whichQuestionFunction,
	listQuestion: listQuestionFunction
}

if __main__ == "__main__":
	# Input
	# Question Classifier
	QuestionType = classifyQuestion()
	# Switch based on question type
		# Function for each question
		# Each question returns an answer
	answer = switch[QuestionType](question)
	print answer
		