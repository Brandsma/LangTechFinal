import requests

def find(string, isProp):
	if isProp:
		params = {'action':'wbsearchentities', 'language':'en', 'format':'json', 'type':'property'}
	else:
		params = {'action':'wbsearchentities', 'language':'en', 'format':'json'}	

	url = 'https://www.wikidata.org/w/api.php'

	params['search'] = string.rstrip()
	json = requests.get(url,params).json()

	returnResult = []
	for result in json['search']:
		returnResult.append(result['id'])

	return returnResult
	#if len(json['search']) > 0:
	#	result = json['search'][0]
	#	return result['id']
