import spacy
from parseNoun import *

nlp = spacy.load("en")

sentence = "What is the capital of the country of the head of state of England?"
res = nlp(sentence)

print(createCombinations(res[3]))


