import sys
import requests
from SPARQLWrapper import SPARQLWrapper, JSON

def getWikidataConcept(word):		
	url = "https://www.wikidata.org/w/api.php"
	params = {'action':'wbsearchentities', 'language':'en', 'format':'json'} #, 'type':'property'}
	params['search'] = word.rstrip()
	json = requests.get(url,params).json()
	return json['search'][0]

def getWikidataProperty(word):		
	url = "https://www.wikidata.org/w/api.php"
	params = {'action':'wbsearchentities', 'language':'en', 'format':'json', 'type':'property'}
	params['search'] = word.rstrip()
	json = requests.get(url,params).json()
	return json['search'][0]

def createQuery(concept, prop):
	query = ("SELECT " + "?targetLabel " + "\n" +
			"WHERE { " + "wd:" + concept + " wdt:" + prop + " ?target" + "\n" +
			
			" SERVICE wikibase:label { bd:serviceParam wikibase:language \"en\". }" + "\n" +
			" }" + " LIMIT 1")
	return query

def fireQuery(query):
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
	# Query request
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	return results
