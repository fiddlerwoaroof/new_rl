import libtcodpy as tc
import libs.combat
import libs.overlay

def trigger_update(func):
	def _inner(self, *a, **kw):
		self.trigger_event('preupdate')
		result = func(self, *a, **kw)
		self.trigger_event('update')
		return result
	return _inner

class Player(libs.overlay.Actor):
	char = ord('@')
	color = (255,255,255)
	light_radius = 10
	def __init__(self, x,y, map, adventurer):
		libs.overlay.Actor.__init__(self, x,y, map, adventurer)
		print 'Player\'s name is %s' % self.adventurer.name
		self.map.set_pov((self.pos, self.light_radius))
		self.display = None

	@trigger_update
	def move(self, dx, dy):
		libs.overlay.Actor.move(self, dx,dy)
		self.map.set_pov((self.pos, self.light_radius))

	def claim_display(self, display):
		self.display = display

	def tick(self):
		return libs.overlay.Actor.tick(self)

class ArrowHandler(object):
	def __init__(self, player, eh):
		self.player = player
		eh.register(tc.KEY_LEFT,self.left)
		eh.register(tc.KEY_RIGHT,self.right)
		eh.register(tc.KEY_UP,self.up)
		eh.register(tc.KEY_DOWN,self.down)

	def do_move(self, shift, dx, dy):
		self.player.add_repeated_action(10 if shift else 1, self.player.move, dx,dy)

	def left(self, alt, shift, ctrl):
		dx,dy = (-1,-1) if alt else (-1,0)
		self.do_move(shift, dx,dy)

	def right(self, alt, shift, ctrl):
		dx,dy = (1,1) if alt else (1,0)
		self.do_move(shift, dx,dy)

	def up(self, alt, shift, ctrl):
		dx,dy = (1,-1) if alt else (0,-1)
		self.do_move(shift, dx,dy)

	def down(self, alt, shift, ctrl):
		dx,dy = (-1,1) if alt else (0,1)
		self.do_move(shift, dx,dy)

