import libtcodpy as tc
import numpy as np

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

class Console(object):
	# TBI: must have a self.con member with the console to be drawn on
	pass

class Screen(object):
	def __init__(self, w, h):
		self.width = w
		self.height = h
		self.con = 0
	def init(self, title, fullscreen=False):
		tc.console_init_root(self.width, self.height, title, fullscreen, 2)
		return self

def squeeze(val, low, high):
	return min(max(val, low), high)

class Map(object):
	def __init__(self, w, h):
		self.width = w
		self.height = h
		self.map = np.random.random_integers(ord('a'), ord('z'), (w,h) )
		self.map[3,5] = ord('*')
		self.map[::10, ::10] = ord('#')
		self.fgcolors = np.random.random_integers(100,255, (w,h,3) )
		self.fgcolors[::10,::10] = (0,0,0)
		self.bgcolors = np.random.random_integers(0,100, (w,h,3) )
		self.bgcolors[::10,::10] = (255,255,255)
		self.overlays = {} # (x,y): { set( object, ... ) }

	def add(self, object):
		self.overlays.setdefault(object.pos,[]).append(object)

	def move(self, object, dx,dy):
		print self.overlays,
		self.overlays[object.pos].remove(object)
		ox,oy = object.pos
		x = squeeze(ox+dx, 0, self.width)
		y = squeeze(oy+dy, 0, self.height)
		self.overlays.setdefault((x,y), []).append(object)
		self.update_overlay(ox,oy)
		return x-ox, y-oy

	def update_overlay(self, x=None, y=None):
		if x is None or y is None: pass
		else:
			if (x,y) in self.overlays and self.overlays[x,y] == []:
				self.overlays.pop((x,y))

	def get_rgb(self, fg=True,slices=(slice(0),slice(0))):
		if fg:
			result = np.rollaxis(self.fgcolors[slices], 2)
		else:
			result = np.rollaxis(self.bgcolors[slices], 2)
		return [x.transpose() for x in result]

	def draw(self, con, tl=(0,0)):
		br = tl[0]+con.width, tl[1]+con.height
		slices = slice(tl[0], tl[0]+con.width), slice(tl[1], tl[1]+con.height)
		tc.console_fill_foreground(con.con, *self.get_rgb(slices=slices))
		tc.console_fill_background(con.con, *self.get_rgb(False,slices=slices))

		chars = np.copy(self.map[slices])
		for x,y in self.overlays:
			screen_x = x-tl[0]
			screen_y = y-tl[1]
			if 0 <= screen_x < con.width and 0 <= screen_y < con.height:
				obj = self.overlays[x,y][-1]
				chars[screen_x,screen_y] = obj.char
				tc.console_set_char_foreground(con.con, screen_x,screen_y, tc.black)
				tc.console_set_char_background(con.con, screen_x,screen_y, tc.white)
		tc.console_fill_char(con.con, chars.transpose())

class EventHandler(object):
	def __init__(self):
		self.key = tc.Key()
		self.mouse = tc.Mouse()
		self.cbs = {}

	def register(self, event, cb):
		self.cbs.setdefault(event,[]).append(cb)

	def tick(self):
		tc.sys_check_for_event(tc.EVENT_KEY_PRESS|tc.EVENT_MOUSE|tc.KEY_PRESSED,
			self.key, self.mouse
		)

		char = chr(self.key.c)
		if char != '\x00' and char in self.cbs:
			for cb in self.cbs[char]:
				cb()

		elif self.key.vk in self.cbs:
			for cb in self.cbs[self.key.vk]:
				cb()



class Application(object):
	def __init__(self):
		self.screen = Screen(200,125)
		self.map = Map(200,125)
		self.player = Player(4,5, self.map)
		self.events = EventHandler()
		ArrowHandler(self.player, self.events)

		tc.sys_set_fps(60)

	def init(self):
		self.screen.init("test")
		self.player.draw()

	def run(self):
		while not tc.console_is_window_closed():
			self.events.tick()
			self.map.draw(self.screen)
			tc.console_print(0, 0,1, '%d' % tc.sys_get_fps())
			tc.console_flush()


if __name__ == '__main__':
	app = Application()
	app.init()
	app.run()
