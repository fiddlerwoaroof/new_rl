from ..dice import MULT, ADD
from .. import dice
from .constants import *

import collections

def health_mod(func):
	def _inner(self):
		mod = 0
		if self.attr.state >= WOUNDED:
			mod = -3
		result = func(self)
		result += mod
		return result
	return _inner

class Skills(object):
	def __init__(self, attr):
		self.skills = {
			'agility','craft','fighting','knowledge',
			'perception','persuasion','shooting','speed',
			'stealth','toughness'
		}
		self.attr = attr
		self.training = Trainer(self)
		self.train = self.training.select

	def check(self, skill, dieroll):
		dieroll.dice = dice.DieJar().d20
		roll = dieroll.roll()
		if roll == 1:
			result = False
		if roll == 20:
			result = True
		else:
			result = roll < getattr(self, skill)
		return result, roll-result # (passes, difference)

	@property
	@health_mod
	def agility(self):
		return (self.attr.dex * 2) + self.training.agility
	@property
	@health_mod
	def craft(self):
		return self.attr.dex + self.attr.int + self.training.craft
	@property
	@health_mod
	def fighting(self):
		return self.attr.str + self.attr.int + self.training.fighting
	@property
	@health_mod
	def knowledge(self):
		return self.attr.int * 2 + self.training.knowledge
	@property
	@health_mod
	def perception(self):
		return self.attr.int + attr.spt + self.training.perception
	@property
	@health_mod
	def persuasion(self):
		return self.attr.spt * 2 + self.training.persuasion
	@property
	@health_mod
	def shooting(self):
		return self.attr.dex + self.attr.int + self.training.shooting
	@property
	@health_mod
	def speed(self):
		return self.attr.str + self.attr.dex + self.training.speed
	@property
	@health_mod
	def stealth(self):
		return self.attr.dex + self.attr.spt + self.training.stealth
	@property
	@health_mod
	def toughness(self):
		return self.attr.str + self.attr.spt + self.training.toughness

class Trainer(object):
	mods = dict(
		untrained=-1,
		familiar=0,
		trained=1,
		experienced=2,
		mastered=3
	)

	def __init__(self, skills):
		self.skills = skills
		self.training = collections.defaultdict(lambda: -1)
		self.points = 500
		self.training_cost = 100

	def select(self, skill, degree):
		if hasattr(degree, 'upper'):
			degree = self.mods.get(degree, 0)
		if self.points >= self.training_cost and degree in self.mods.values():
			self.training[skill] = degree
			self.points -= self.training_cost

	def __getattr__(self, key):
		skills = object.__getattribute__(self, 'skills')
		if key in self.skills.skills:
			return self.training[key]
		else:
			raise
	def __setattr__(self, key, value):
		if hasattr(self, 'skills') and key in self.skills.skills:
			if -1 <= value <= 3:
				self.training[key] = int(round(value))
			else:
				raise AttributeError(
					'cannot set training of %s to %d, (out of range [-1,3])' % (key, value)
				)
		else:
			object.__setattr__(self, key, value)


