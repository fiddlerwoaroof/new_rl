import numpy as np
import libtcodpy as tc

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
