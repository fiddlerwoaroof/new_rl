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
		if event not in self.events:
			raise ValueError('%r has no event %r' % (self, event))

		for cb in self.events[event]:
			result = cb(self, *args, **kw)
			result = result is None or result # if the event returns a false value besides None, break
			if result == False: break

	handled_events = collections.OrderedDict()
	@classmethod
	def handle_event(cls, event):
		def _inner(cb):
			cls.handled_events.setdefault(event, []).append(cb)
			return cb
		return _inner



class Actor(Overlay):
	char = ord('@')
	color = (255,0,0)
	blocks = True

	@property
	def pos(self):
		return self.x, self.y

	def __init__(self, x,y, map, adventurer=None):
		super(Actor, self).__init__(x,y, map)
		self.inventory = []
		if adventurer is None:
			adventurer = combat.Adventurer.randomize()
		self.adventurer = adventurer

	def move(self, dx, dy):
		dx, dy = self.map.move(self, dx,dy)
		self.x += dx
		self.y += dy

	def tick(self):
		result = True
		if self.adventurer.state >= 2:
			result = False
			self.char = ord('%')
			self.blocks = False
		return result

	def ishostile(self, other):
		return self.adventurer.state < 2 #TODO: implement factions

	def bump(self, other):
		print '%s bumped %s' % (type(self).__name__, type(other).__name__)
		if isinstance(other, Actor) and other.ishostile(self):
			self.adventurer.attack(other.adventurer)
			other.trigger_event('attacked', self)
		elif isinstance(other, Object):
			self.pickup(other)
			other.trigger_event('picked_up', self)

		other.trigger_event('bumped', self)

	@Overlay.handle_event('attacked')
	def attacked_by(self, other):
		if self.adventurer.skills.check('agility'):
			self.adventurer.attack(other.adventurer)

	@Overlay.handle_event('bumped')
	def bumped_by(self, other):
		print '%s was bumped by %s' % (type(self).__name__, type(other).__name__)

class Object(Overlay):
	item = None
	@Overlay.handle_event('picked_up')
	def picked_up_by(self, other):
		self.map.remove(self)

class Weapon(Object):
	item = None

class Potion(Object):
	char = ord('!')

class Scroll(Object):
	char = ord('!')

class Equipment(Object):
	pass
