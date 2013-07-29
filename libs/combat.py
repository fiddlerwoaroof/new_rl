from . import dice

from .combat_parts import races
from .combat_parts import equipment
from .combat_parts import skills
from .combat_parts import constants as const

import collections

class Attributes(object):
	def __init__(self, strength, intellect, dexterity, spirit):
		self.str = strength
		self.int = intellect
		self.dex = dexterity
		self.spt = spirit
		self.state = const.HEALTHY


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

	def __init__(self, name, race, str, int, dex, spt):
		self.name = name
		self.attributes = Attributes(str, int, dex, spt)
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

		result, damage = self.skills.check('toughness', dieroll)

		if not result:
			if damage > 0:
				self.state += 1
				print '%s takes %d damage and is now %s' % (self.name, damage, ['healthy', 'wounded', 'ko'][self.state if self.state < 3 else 2])
				if self.state >= const.KNOCKOUT:
					self.die()

	def die(self): pass

def get_stats():
	stats = [7,7,7,7]
	import random
	mod = +1
	for x in range(100):
		idx = random.choice([x for x in range(len(stats)) if stats[x] > 5])
		stats[idx] += mod
		mod *= -1
	print sum(stats), stats
	return stats

if __name__ == '__main__':
	a = Adventurer('bob', 'elf', *get_stats())
	b = Adventurer('bill', 'elf', *get_stats())

	while const.KNOCKOUT not in {a.state, b.state}:
		a.attack(b)
		b.attack(a)

	print a.name, 'is', ['healthy', 'wounded', 'ko'][a.state if a.state < 3 else 2]
	print b.name, 'is', ['healthy', 'wounded', 'ko'][b.state if b.state < 3 else 2]
