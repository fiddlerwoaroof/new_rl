from src import events
import abc
import collections
from . import combat

class Overlay(object):
	__metaclass__ = abc.ABCMeta

	char = abc.abstractproperty()
	color = (0,0,0)
	blocks = False

	@property
	def pos(self):
		return self.x, self.y
	def __init__(self, x,y, map):
		super(Overlay, self).__init__()
		print self.handled_events
		self.events = collections.OrderedDict()
		self.x = x
		self.y = y
		self.map = map
		for key, value in self.handled_events.viewitems():
			self.events.setdefault(key, []).extend(value)

	def draw(self):
		self.map.add(self)

	def register_event(self, event, cb):
		'''register a callback for an event

		if the callback returns a false value besides None, execution will end after that event'''
		self.events.setdefault(event, []).append(cb)

	def trigger_event(self, event, *args, **kw):
		for cb in self.events.get(event, []):
			result = cb(self, *args, **kw)
			result = result is None or result # if the event returns a false value besides None, break
			if result == False: break

	@staticmethod
	def add_event(event,  cb_name):
		def _inner(cls):
			if not hasattr(cls,  'handled_events'):
				cls.handled_events = {}
				for base in cls.bases:
					if hasattr(base,  'handled_events'):
						cls.handled_events.update(base.handled_events)
			cls.handled_events.setdefault(event,  []).append(getattr(cls,  cb_name))
			return cls
		return _inner

	def tick(self):
		pass


@Overlay.add_event('attacked',  'attacked_by')
@Overlay.add_event('bumped',  'bumped_by')
class Actor(Overlay):
	char = ord('@')
	color = (255,0,0)
	blocks = True

	handled_events = collections.OrderedDict()
	@property
	def pos(self):
		return self.x, self.y

	def __init__(self, x,y, map, adventurer=None):
		super(Actor, self).__init__(x,y, map)
		self.inventory = []
		if adventurer is None:
			adventurer = combat.Adventurer.randomize()
		self.adventurer = adventurer
		self.repeated_actions = {}

	def add_repeated_action(self, time, action, *args, **kw):
		print 'adding action', action, args, kw
		self.repeated_actions.setdefault(time, []).append( (action, args, kw) )

	def update_pos(self, dx,dy):
		self.x += dx
		self.y += dy

	def move(self, dx, dy):
		print 'moving'
		return self.map.move(self, dx,dy, self.update_pos)


	def tick(self):
		result = True
		if self.adventurer.state >= 2:
			result = False
			self.char = ord('%')
			self.blocks = False
		else:
			self.act()
			ractions = {}
			for nleft, actions in self.repeated_actions.items():
				for (action,args,kwargs) in actions:
					print action,args,kwargs
					action(*args, **kwargs)
					if nleft > 1:
						ractions.setdefault(nleft-1, []).append( (action,args,kwargs) )
				print ractions
			self.repeated_actions = ractions
		return result

	def act(self): pass

	def ishostile(self, other):
		return self.adventurer.state < 2 #TODO: implement factions

	def bump(self, other):
		print '%s bumped %s' % (type(self).__name__, type(other).__name__)
		if isinstance(other, Actor) and other.ishostile(self):
			self.adventurer.attack(other.adventurer)
			other.trigger_event('attacked', self)

	def interact(self, other):
		result = False
		if isinstance(other, Object):
			result = True
			self.pickup(other)
			other.trigger_event('picked_up', self)

		other.trigger_event('bumped', self)
		return result

	def pickup(self, other):
		self.inventory.append(other)

	def attacked_by(self, other):
		if self.adventurer.skills.check('agility'):
			self.adventurer.attack(other.adventurer)

	def bumped_by(self, other):
		print '%s was bumped by %s' % (type(self).__name__, type(other).__name__)

import random
class AIActor(Actor):
	def act(self):
		print 'wiggly %s' % self.adventurer.name
		self.move(random.choice([-1,0,1]), random.choice([-1,0,1]))

@Overlay.add_event('picked_up',  'picked_up_by')
@Overlay.add_event('bumped',  'bumped_by')
class Object(Overlay):
	item = None
	handled_events = collections.OrderedDict()
	def picked_up_by(self, other):
		events.EventHandler().trigger_event('msg', 'picked up a %s' % self)
		self.map.remove(self)
	def bumped_by(self, other): pass

class Weapon(Object):
	item = None

class Potion(Object):
	char = ord('!')
	def __str__(self): return 'potion'

class Scroll(Object):
	char = ord('!')

class Equipment(Object):
	pass
