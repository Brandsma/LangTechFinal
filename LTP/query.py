import requests

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
		query = '''SELECT '''
		for var in varToBeShown:
			query += var + '''Label '''
		query += '''WHERE {'''

	query += statement + ''' '''

	query += '''SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}'''
	if varToBeShown != []:
		query += ''' LIMIT 100'''
	return query

def sendQuery(query):
	url = 'https://query.wikidata.org/sparql';
	return requests.get(url, params={'query': query, 'format': 'json'}).json();

def replaceQuery(query, i, replaceDictionary):
	j = 0
	m = i	
	query1 = query
	for k, v in replaceDictionary.items():
		#print(k, ", ", v[m%3])
		#print(query)
		query1 = query1.replace(k, v[0] + v[1][m%3])#"wd:"+v[m%3])
		j += 1
		m = int(m/3)
	return query1

def formatResults(results):
	print(results)
	if 'boolean' in results: #results == "true" or results == "false":
		return [results['boolean']]

	returnResult = []
	for item in results['results']['bindings']:
		li = {}
		string = ""
		for var in item :
			li[var] = item[var]['value']
			#string += li[var] + "\t"				
			#print(li[var], "\t")
		#string += "\n"
		#print(string)
		returnResult.append(li)
	#print(returnResult)
	for result in returnResult:
		for k, v in result.items():
			print(v, "\t")
	return returnResult
	

def fireQuery(query, replaceDictionary):
	result = []
	rq = Query(query, replaceDictionary)
	while rq.hasNext():
		query1 = rq.getNext()
		print("\n\n\n")
		print(query1)
		print("\n\n\n")
		data = sendQuery(query1)
		result = formatResults(data)
		if result != [] and (('boolean' in result) == False or result['boolean'] != ["false"]):
			return result
	if (('boolean' in result) == True and result['boolean'] == ["false"]):
		return result
	raise ValueError
