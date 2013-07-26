import libtcodpy as tc

class Player(object):
	@property
	def pos(self):
		return self.x, self.y

	def __init__(self, x,y, map):
		self.x = x
		self.y = y
		self.char = ord('@')
		self.color = tc.Color(255,255,255)
		self.map = map

	def draw(self):
		self.map.add(self)

	def move(self, dx, dy):
		print self.pos,
		dx, dy = self.map.move(self, dx,dy)
		self.x += dx
		self.y += dy
		print self.pos

class ArrowHandler(object):
	def __init__(self, player, eh):
		self.player = player
		eh.register(tc.KEY_LEFT,self.left)
		eh.register(tc.KEY_RIGHT,self.right)
		eh.register(tc.KEY_UP,self.up)
		eh.register(tc.KEY_DOWN,self.down)
	def left(self):
		print 'left'
		self.player.move(-1, 0)
	def right(self):
		print 'right'
		self.player.move(1, 0)
	def up(self):
		print 'up'
		self.player.move(0, -1)
	def down(self):
		print 'down'
		self.player.move(0, 1)

