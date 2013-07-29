from . import dice
from .dice import MULT,ADD
from . import type_dict

import collections

class Attributes(object):
	def __init__(self, strength, intellect, dexterity, spirit):
		self.str = strength
		self.int = intellect
		self.dex = dexterity
		self.spt = spirit
		self.state = HEALTHY

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


class Equipment(object): pass
class Weapon(Equipment): pass
class Armor(Equipment): pass


class Slot(object):
	def __init__(self, name, type):
		self.name = name
		self.attr = 'slotted_%s' % name
		self.type = type

	def __get__(self, instance, owner):
		return self.getitem(instance)
	def __set__(self, instance, value):
		self.setitem(instance, value)

	def setitem(self, instance, value):
		if isinstance(value, self.type):
			setattr(instance, 'slotted_%s' % self.name, value)
		else:
			raise ValueError(
				'Can\'t use an object of type %s in a slot of type %s' % (type(value), self.type)
			)


	def getitem(self, instance):
		return getattr(instance, self.attr, None)

	def filled(self, instance):
		return self.getitem(instance) is not None

	@classmethod
	def add_slot(cls, name, type):
		def _inner(to_cls):
			inst = cls(name, type)
			setattr(to_cls, name, inst)
			if not hasattr(to_cls, 'equipment_slots'):
				to_cls.equipment_slots = Slots((name,inst))
			else:
				to_cls.equipment_slots[name] = inst
			return to_cls
		return _inner


class Slots(collections.MutableMapping):
	def __init__(self, *args, **kw):
		self.slots = dict(args)
		self.slots.update(kw)
		self.slots_by_type = type_dict.TypeDict(__default=[])
		for k in self.slots:
			slot = self.slots[k]
			self.slots_by_type[slot.type].append(slot)

	def __getitem__(self, key):
		return self.slots[key]
	def __setitem__(self, k, v):
		self.slots[k] = v
	def __delitem__(self, key):
		del self.slots[key]

	def __iter__(self):
		return iter(self.slots)
	def __len__(self):
		return len(self.slots)

	def slots_of_type(self, slot_type):
		return self.slots_by_type[slot_type]

class Race(object):
	registry = {}
	@classmethod
	def register(cls, new):
		cls.registry[new.__name__.lower()] = new

	@classmethod
	def random_race(cls):
		return random.choice(self.registry.values())
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
	def mod(self, atr):
		attr.str += 1

@Race.register
class Hobbit(Race):
	allowed_professions = {'thief', 'barbarian'}
	def mod(self, atr):
		attr.dex += 1


class Sword(Weapon):
	attack = 1
	damage_mod = 1


HEALTHY = 0
WOUNDED = 1
KNOCKOUT = 2

@Slot.add_slot('weapon', Weapon)
@Slot.add_slot('armor', Armor)
class Adventurer(object):
	@property
	def state(self):
		return self.attributes.state
	@state.setter
	def state(self, val):
		if val not in {HEALTHY, WOUNDED, KNOCKOUT}:
			raise ValueError('Value for state invalid')
		self.attributes.state = val

	def __init__(self, name, race, str, int, dex, spt):
		self.name = name
		self.attributes = Attributes(str, int, dex, spt)
		self.skills = Skills(self.attributes)
		self.race = Race.registry[race](self.attributes)

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
				if self.state >= KNOCKOUT:
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


a = Adventurer('bob', 'elf', *get_stats())
b = Adventurer('bill', 'elf', *get_stats())

while KNOCKOUT not in {a.state, b.state}:
	a.attack(b)
	b.attack(a)

print a.name, 'is', ['healthy', 'wounded', 'ko'][a.state if a.state < 3 else 2]
print b.name, 'is', ['healthy', 'wounded', 'ko'][b.state if b.state < 3 else 2]
