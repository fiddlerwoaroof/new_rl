import abc

class Overlay(object):
	__metaclass__ = abs.ABCMeta

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

	def draw(self):
		self.map.add(self)

	def move(self, dx, dy):
		dx, dy = self.map.move(self, dx,dy)
		self.x += dx
		self.y += dy

	def tick(self):
		pass


	def bump(self, other):
		print '%s bumped %s' % (type(self).__name__, type(other).__name__)
		other.bumped_by(self)
	def bumped_by(self, other):
		print '%s was bumped by %s' % (type(self).__name__, type(other).__name__)

class Object(Overlay):
	pass


class Potion(Object):
	char = ord('!')
class Scroll(Object):
	char = ord('!')
