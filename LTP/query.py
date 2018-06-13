import requests
import traceback

from replaceQuery import *

def createQuery(dict):
	varToBeShown = dict["varToBeShown"]
	statement = dict["statement"]

	varToBeShown1 = []
	for var in varToBeShown:
		if (var in varToBeShown1) == False:
			varToBeShown1.append(var)
	varToBeShown = varToBeShown1

	if varToBeShown == []:
		query = '''ASK {'''
	else:
		query = '''SELECT distinct '''
		for var in varToBeShown:
			if var.startswith("(count"):
				query += var
			else:
				query += var + '''Label '''
		query += '''WHERE {'''

	query += statement + ''' '''

	query += '''SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}'''

	return query

def sendQuery(query):
	url = 'https://query.wikidata.org/sparql';
	return requests.get(url, params={'query': query, 'format': 'json'}).json();

def replaceQuery(query, i, replaceDictionary):
	j = 0
	m = i	
	query1 = query
	for k, v in replaceDictionary.items():
		query1 = query1.replace(k, v[0] + v[1][m%3])#"wd:"+v[m%3])
		j += 1
		m = int(m/3)
	return query1

def formatResults(results):
	if 'boolean' in results: #results == "true" or results == "false":
		return [results['boolean']]

	returnResult = []
	for item in results['results']['bindings']:
		li = {}
		string = ""
		for var in item :
			li[var] = item[var]['value']
			string += li[var] + "\t"				
		returnResult.append(string)
	return returnResult
	

def fireQuery(query, replaceDictionary):
	result = []
	rq = Query(query, replaceDictionary)
	while rq.hasNext():
		query1 = rq.getNext()
		try:
			data = sendQuery(query1)
			result = formatResults(data)
			if result != [] and result != [False] and result != ["0\t"]:
				return result
		except Exception:
			pass
	if (result == [False]):
		return result
	raise ValueError
