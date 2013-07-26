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
		self.color = (255,255,255)
		self.map = map
	def move(self, dx, dy):
		self.map.move(self, dx,dy)
		self.x += dx
		self.y += dy

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

class Map(object):
	def __init__(self, w, h):
		self.width = w
		self.height = h
		self.map = np.random.random_integers(ord('a'), ord('z'), (w,h) )
		self.fgcolors = np.random.random_integers(100,255, (w,h,3) )
		self.bgcolors = np.random.random_integers(0,100, (w,h,3) )
		overlays = {} # (x,y): { set( (char,fg), ... ) }

	def move(self, object, dx,dy):
		overlays[object.pos].remove(object)
		ox,oy = object.pos
		x = ox+dx
		y = oy+dy
		if 0 < x < self.width and 0 < y < self.height:
			self.overlays[x,y] = object
			return x,y
		#elif 

	def get_rgb(self, fg=True,slices=(slice(0),slice(0))):
		if fg:
			return np.rollaxis(self.fgcolors[slices], 2)
		else:
			return np.rollaxis(self.bgcolors[slices], 2)

	def draw(self, con, tl=(0,0)):
		br = tl[0]+con.width, tl[1]+con.height
		slices = tuple(map(slice, tl,br))
		tc.console_fill_foreground(con.con, *self.get_rgb(slices=slices))
		tc.console_fill_background(con.con, *self.get_rgb(False,slices=slices))
		tc.console_fill_char(con.con, self.map[slices])

class EventHandler(object):
	def __init__(self):
		self.key = tc.Key()
		self.mouse = tc.Mouse()
		self.cbs = {}

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
		self.screen = Screen(120,75)
		self.map = Map(120,78)
		self.player = Player(40,25, self.map)
		self.events = EventHandler()

		tc.sys_set_fps(60)

	def init(self):
		self.screen.init("test")

	def run(self):
		while not tc.console_is_window_closed():
			self.events.tick()
			self.map.draw(self.screen)
			tc.console_print(0, 0,0, '%d' % tc.sys_get_fps())
			tc.console_flush()


if __name__ == '__main__':
	app = Application()
	app.init()
	app.run()
