import libtcodpy as tc

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
