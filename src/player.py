import libtcodpy as tc
import libs.combat
import libs.overlay

vowels = {'a', 'e', 'i', 'o', 'u'}
def shorten(str):
	init = str[0]
	fin = ''
	middle = ''
	if len(str) > 1:
		fin = str[-1]
	if len(str) > 2:
		middle = ''.join(x for x in str[1:-1] if x not in vowels)
	return '%s%s%s' % (init, middle, fin)

class _CancelUpdate: pass
def trigger_update(func):
	def _inner(self, *a, **kw):
		result = func(self, *a, **kw)
		if result is not _CancelUpdate:
			#print 'will update!'
			self.update = True
		return result
	return _inner

@libs.overlay.Actor.add_event('attack', 'attack')
class Player(libs.overlay.Actor):
	char = ord('@')
	color = (255,255,255)
	light_radius = 10
	def __init__(self, x,y, map, adventurer):
		libs.overlay.Actor.__init__(self, x,y, map, adventurer)
		#print 'Player\'s name is %s' % self.adventurer.name
		self.map.set_pov((self.pos, self.light_radius))
		self.display = None
		self.update = False

	@trigger_update
	def attack(self, *a, **kw):
		print 'attack'

	@trigger_update
	def move(self, dx, dy):
		dx,dy = libs.overlay.Actor.move(self, dx,dy)
		if (dx,dy) != (0,0):
			self.map.set_pov((self.pos, self.light_radius))
		else:
			return _CancelUpdate
		return dx,dy

	def claim_display(self, display):
		self.display = display

	def tick(self):
		self.display.set_line(0, shorten(self.adventurer.name))
		self.display.set_line(1, self.adventurer.readable_state)

		result = libs.overlay.Actor.tick(self)
		if self.update:
			#print 'updating'
			try: self.trigger_event('update')
			finally: self.update = False

		return result


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

