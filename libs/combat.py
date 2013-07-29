from . import dice

from .combat_parts import races
from .combat_parts import equipment
from .combat_parts import skills
from .combat_parts import constants as const

import collections
import random

def get_stats(sum_):
	stats = [sum_/4]*4
	if sum(stats) != sum_:
		stats[0] += sum_ - sum(stats)

	mod = +1
	for x in range(100):
		idx = random.choice([x for x in range(len(stats)) if stats[x] > 3])
		stats[idx] += mod
		mod *= -1
	return stats

class Attributes(object):
	@classmethod
	def randomize(cls, sum_):
		chosen_stats = get_stats(sum_)
		return cls(*chosen_stats)

	def __init__(self, strength, intellect, dexterity, spirit):
		self.str = strength
		self.int = intellect
		self.dex = dexterity
		self.spt = spirit
		self.state = const.HEALTHY
	def __str__(self):
		return '%s %s %s %s %s' % (self.str, self.int, self.dex, self.spt, self.state)


@equipment.Slot.add_slot('weapon', equipment.Weapon)
@equipment.Slot.add_slot('armor', equipment.Armor)
class Adventurer(object):
	@property
	def state(self):
		return self.attributes.state
	@state.setter
	def state(self, val):
		if val not in {const.HEALTHY, const.WOUNDED, const.KNOCKOUT}:
			raise ValueError('Value for state invalid')
		self.attributes.state = val

	@classmethod
	def randomize(cls, stat_sum=28):
		name = '%s %s%s' % (
			random.choice(['Bill', 'Bob', 'Jerry']),
			random.choice(['Longnose', 'Short-Tail', 'Squint']),
			random.choice(['', ' the Great', ' The Cross-eyed', ' The Magnificent'])
		)
		race = races.Race.random_race()
		attr = Attributes.randomize(stat_sum)
		print attr
		return cls(name, race, attr)

	@classmethod
	def with_stats(cls, name, race, str, int, dex, spt):
		attr = Attributes(str, int, dex, spt)
		return cls(name, race, attr)

	def __init__(self, name, race, attr):
		self.name = name
		self.attributes = attr
		self.skills = skills.Skills(self.attributes)
		self.race = races.Race.registry[race](self.attributes)

	def wield(self, slot, equipment):
		turns = 1
		if self.equipment_slots[slot].filled(self):
			turns += 1
		self.equipment_slots[slot].setitem(self, equipment)
		return turns

	def attack(self, opponent, type='fighting', num_allies=0):
		dieroll = dice.DieRoll()

		ally_bonus = -1 if num_allies > 0 else 0
		# TODO: implement professions, figure out how to mod ally_bonus for thieves cleanly
		dieroll.add_adjustment(add=ally_bonus)

		pass_, damage = self.skills.check(type, dieroll)
		if pass_:
			if self.weapon is not None:
				damage += self.weapon.damage_mod
			print '%s inflicts %d damage upon %s' % (self.name, damage, opponent.name)
			opponent.take_damage(damage)

	def take_damage(self, damage):
		if self.armor is not None:
			damage += self.armor.damage_mod

		dieroll = dice.DieRoll()
		dieroll.add_adjustment(-damage)

		result, __ = self.skills.check('toughness', dieroll)

		if not result:
			if damage > 0:
				self.state += 1
				print '%s takes %d damage and is now %s' % (self.name, damage, ['healthy', 'wounded', 'ko'][self.state if self.state < 3 else 2])
				if self.state >= const.KNOCKOUT:
					self.die()

	def die(self): pass

if __name__ == '__main__':
	a = Adventurer.randomize(28)
	b = Adventurer.randomize(28)

	while const.KNOCKOUT not in {a.state, b.state}:
		a.attack(b)
		b.attack(a)

	print a.name, 'is', ['healthy', 'wounded', 'ko'][a.state if a.state < 3 else 2]
	print b.name, 'is', ['healthy', 'wounded', 'ko'][b.state if b.state < 3 else 2]
