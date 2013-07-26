import libtcodpy as tc

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



