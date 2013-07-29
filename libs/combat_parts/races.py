import random

class Race(object):
	registry = {}
	@classmethod
	def register(cls, new):
		cls.registry[new.__name__.lower()] = new

	@classmethod
	def random_race(cls):
		return random.choice(cls.registry.keys())

	@property
	def name(self):
		return self.__class__.__name__.lower()

	allowed_professions = set()
	def __init__(self, attr):
		self.mod(attr)

	def allows_profession(self, prof):
		return prof in self.allowed_professions

@Race.register
class Human(Race):
	def mod(self, attr):
		attr.spt += 1

@Race.register
class Elf(Race):
	allowed_professions = {'fighter', 'wizard', 'thief'}
	def mod(self, attr):
		attr.int += 1

@Race.register
class Dwarf(Race):
	allowed_professions = {'fighter', 'Priest', 'thief'}
	def mod(self, attr):
		attr.str += 1

@Race.register
class Hobbit(Race):
	allowed_professions = {'thief', 'barbarian'}
	def mod(self, attr):
		attr.dex += 1



