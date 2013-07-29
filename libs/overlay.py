import abc
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
		self.x = x
		self.y = y
		self.map = map
	def draw(self):
		self.map.add(self)


class Actor(Overlay):
	char = ord('@')
	color = (255,0,0)
	blocks = True

	@property
	def pos(self):
		return self.x, self.y

	def __init__(self, x,y, map, adventurer=None):
		self.x = x
		self.y = y
		self.map = map
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
		return True #TODO: implement factions

	def bump(self, other):
		print '%s bumped %s' % (type(self).__name__, type(other).__name__)
		if isinstance(other, Actor) and other.ishostile(self):
			self.adventurer.attack(other.adventurer)
			other.attacked_by(self)
		other.bumped_by(self)

	def attacked_by(self, other):
		if self.adventurer.skills.check('agility'):
			self.adventurer.attack(other.adventurer)

	def bumped_by(self, other):
		print '%s was bumped by %s' % (type(self).__name__, type(other).__name__)

class Object(Overlay):
	pass


class Potion(Object):
	char = ord('!')
class Scroll(Object):
	char = ord('!')
