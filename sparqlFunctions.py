import sys
import requests
from SPARQLWrapper import SPARQLWrapper, JSON

def getWikidataConcept(word):		
	url = "https://www.wikidata.org/w/api.php"
	params = {'action':'wbsearchentities', 'language':'en', 'format':'json'} #, 'type':'property'}
	params['search'] = word.rstrip()
	json = requests.get(url,params).json()
	try:
		return json['search'][0]
	except Exception:
		return getWikidataConcept("Douglas Adams")

def getWikidataProperty(word):		
	url = "https://www.wikidata.org/w/api.php"
	params = {'action':'wbsearchentities', 'language':'en', 'format':'json', 'type':'property'}
	params['search'] = word.rstrip()
	json = requests.get(url,params).json()
	try:
		return json['search'][0]
	except Exception:
		return getWikidataProperty("Instance Of")

def fireQuery(query):
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
	# Query request
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	return results