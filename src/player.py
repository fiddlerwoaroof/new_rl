import libtcodpy as tc
import libs.combat
import libs.overlay

class Player(libs.overlay.Actor):
	char = ord('@')
	color = (255,255,255)
	light_radius = 10
	def __init__(self, x,y, map, adventurer):
		libs.overlay.Actor.__init__(self, x,y, map, adventurer)
		self.map.set_pov((self.pos, self.light_radius))
	def move(self, dx, dy):
		libs.overlay.Actor.move(self, dx,dy)
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

