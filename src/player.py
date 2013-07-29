import libtcodpy as tc
import libs.combat

class Actor(object):
	char = ord('@')
	color = (255,0,0)
	blocks = True

	@property
	def pos(self):
		return self.x, self.y

	def __init__(self, x,y, map):
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

class Player(Actor):
	char = ord('@')
	color = (255,255,255)
	light_radius = 10
	def __init__(self, x,y, map):
		Actor.__init__(self, x,y, map)
		self.map.set_pov((self.pos, self.light_radius))
	def move(self, dx, dy):
		Actor.move(self, dx,dy)
		self.map.set_pov((self.pos, self.light_radius))

class ArrowHandler(object):
	def __init__(self, player, eh):
		self.player = player
		eh.register(tc.KEY_LEFT,self.left)
		eh.register(tc.KEY_RIGHT,self.right)
		eh.register(tc.KEY_UP,self.up)
		eh.register(tc.KEY_DOWN,self.down)
	def left(self, alt, shift, ctrl):
		val = 10 if shift else 1
		if alt:
			self.player.move(-val, -val)
		else:
			self.player.move(-val, 0)
	def right(self, alt, shift, ctrl):
		val = 10 if shift else 1
		if alt:
			self.player.move(val, val)
		else:
			self.player.move(val, 0)
	def up(self, alt, shift, ctrl):
		val = 10 if shift else 1
		if alt:
			self.player.move(val, -val)
		else:
			self.player.move(0, -val)
	def down(self, alt, shift, ctrl):
		val = 10 if shift else 1
		if alt:
			self.player.move(-val, val)
		else:
			self.player.move(0, val)

