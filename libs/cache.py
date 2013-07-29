class Cache(object):
	def __init__(self):
		self.cache = {}
	def add(self, key, value):
		self.cache[key] = value
	def get(self, key, cb):
		if key not in self.cache:
			self.add(key, cb())
		return self.cache[key]
