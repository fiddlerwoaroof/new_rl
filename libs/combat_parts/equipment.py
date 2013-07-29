from .. import type_dict

import collections

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

class Sword(Weapon):
	attack = 1
	damage_mod = 1


