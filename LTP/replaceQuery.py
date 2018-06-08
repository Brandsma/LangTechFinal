class Query(object):
	query = ""
	replaceDictionary = {}
	i = 0
	n = {}
	totalN = 1;
	MAX_OPTIONS = 3

	def __init__(self, query, replaceDictionary):
		self.query = ""
		self.replaceDictionary = {}
		self.i = 0
		self.n = {}
		self.totalN = 1;
		self.MAX_OPTIONS = 3
		self.query = query
		self.replaceDictionary = replaceDictionary
		self.countCombinations()
		
	def countCombinations(self):
		for k, v in self.replaceDictionary.items():
			if isinstance(v[1], str):
				self.n[k] = 1
				self.replaceDictionary[k] = (v[0], [v[1]])
			elif len(v[1]) > self.MAX_OPTIONS:
				self.n[k] = self.MAX_OPTIONS
			else:
				self.n[k] = len(v[1])
			print("\n\n n:"+ k + " " + str(len(v[1])) + " " + str(self.n[k]))
			self.totalN *= self.n[k]
		if self.totalN == 0:
			raise ValueError

	def getNext(self):
		print(self.replaceDictionary)
		print("\n\n\n")
		print(self.n)
		m = self.i
		query1 = self.query
		for k, v in self.replaceDictionary.items():
			#print(k, ", ", v[m%self.n[k]])
			#print(query)
			query1 = query1.replace(k + " ", v[0] + v[1][m%self.n[k]] + " ")
			query1 = query1.replace(k + ".", v[0] + v[1][m%self.n[k]] + ".")
			query1 = query1.replace(k + "}", v[0] + v[1][m%self.n[k]] + "}")
			query1 = query1.replace(k + ")", v[0] + v[1][m%self.n[k]] + ")")#"wd:"+v[m%3])
			m = int(m/self.n[k])
		self.i += 1
		return query1

	def hasNext(self):
		print(str(self.i) + " totalN " + str(self.totalN))
		return self.i < self.totalN
