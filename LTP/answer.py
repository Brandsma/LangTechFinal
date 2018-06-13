from dependency import *
from parseVerb import *
from query import *

def answer(question):
	try:
		result = createDependencyTree(question)
		root = findRoot(result)
		res = parseVerb(root, None)
		query = createQuery(res)
		queryResult = fireQuery(query, res["replaceDictionary"])
	except:
		queryResult = []
	return queryResult
