import libtcodpy as tc
import collections

class EventHandler(object):
	events = {}
	def register_event(self, event):
		return self.events.setdefault(event, [])
	def handle_event(self, event, cb, *a, **kw):
		cbs = self.register_event(event)
		cbs.append( (cb, a, kw) )
	def trigger_event(self, event, *a, **kw):
		for cb, args, kwargs in self.events.get(event,[]):
			kw.update(kwargs)
			a += args
			result = cb(*a, **kw)
			if result is not None and not result: break


class TCODEventHandler(object):
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

		alt, shift, ctrl = self.key.lalt|self.key.ralt, self.key.shift, self.key.lctrl|self.key.rctrl
		char = chr(self.key.c)
		if char != '\x00' and char in self.cbs:
			for cb in self.cbs[char]:
				cb(alt,shift,ctrl)

		elif self.key.vk in self.cbs:
			for cb in self.cbs[self.key.vk]:
				cb(alt,shift,ctrl)



