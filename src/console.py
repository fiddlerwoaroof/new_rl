import libtcodpy as tc
import numpy as np

class Console(object):
	# TBI: must have a self.con member with the console to be drawn on
	@property
	def dim(self):
		return self.width, self.height

	def __init__(self, w,h, parent=None, offset=(0,0)):
		self.width = w
		self.height = h
		self.offset = offset
		self.parent = parent

		if parent is None:
			self.con = 0
		else:
			self.con = tc.console_new(w,h)

	def blit(self):
		if self.parent is not None:
			xdst,ydst = self.offset
			tc.console_blit(self.con, 0,0, self.width, self.height, self.parent.con, xdst,ydst)

	def set_bg(self, r,g,b):
		tc.console_set_default_background(self.con, r,g,b)

	def set_fg(self, r,g,b):
		tc.console_set_default_foreground(self.con, r,g,b)

	def clear(self):
		tc.console_clear(self.con)

	def fill(self, r,g,b):
		r = np.ones(self.dim) * r
		g = np.ones(self.dim) * g
		b = np.ones(self.dim) * b
		tc.console_fill_background(self.con, r,g,b)

	def print_(self, pos, msg, *fmt):
		x,y = pos
		tc.console_print(self.con, x,y, msg % fmt)




class Screen(Console):
	# Root console
	def init(self, title, fullscreen=False):
		tc.console_init_root(self.width, self.height, title, fullscreen, 2)
		return self

	def flush(self):
		tc.console_flush()
