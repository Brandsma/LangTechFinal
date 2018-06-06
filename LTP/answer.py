from dependency import *
from parseVerb import *
from query import *

def answer(question):
	result = createDependencyTree(question)
	root = findRoot(result)
	res = parseVerb(root, None)
	print(res)
	query = createQuery(res)
	queryResult = fireQuery(query, res["replaceDictionary"])
	return queryResult
