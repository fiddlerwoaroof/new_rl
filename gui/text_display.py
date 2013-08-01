import src.console
import collections

class MessageBox(object):
	def __init__(self, console, num, pos, event=None):
		self.console = console
		self.pos = x,y = pos
		self.messages = collections.deque([], num)
		self.maxlen = -float('inf')
		if event is not None:
			import src.events
			src.events.EventHandler().handle_event(event, self.msg)

	def msg(self, msg, *a):
		msg %= a
		self.messages.append(msg)
		self.maxlen = max(self.maxlen, len(msg))
		x,y = self.pos
		for idx, msg in enumerate(self.messages):
			self.console.print_( (x,y+idx), msg.ljust(self.maxlen) )
		return False

class TextBox(object):
	def __init__(self, console, num, pos, event=None):
		self.console = console
		self.pos = x,y = pos
		self.lines = [''] * num
		self.maxlen = -float('inf')
		if event is not None:
			import src.events
			src.events.EventHandler().handle_event(event, self.set_line)

	def set_line(self, line, msg, *a):
		msg = msg % a
		self.maxlen = max(self.maxlen, len(msg))
		self.lines[line] = msg
		x,y = self.pos
		self.console.print_( (x,y+line), msg.ljust(self.maxlen) )
		return False

class Label(object):
	def __init__(self, console, pos, event=None):
		self.console = console
		self.pos = x,y = pos
		self.line = ''
		self.maxlen = -float('inf')
		if event is not None:
			import src.events
			src.events.EventHandler().handle_event(event, self.set_text)
	def set_text(self, msg, *a):
		msg = msg % a
		self.maxlen = max(self.maxlen, len(msg))
		self.line = msg
		x,y = self.pos
		self.console.print_( (x,y), msg.ljust(self.maxlen) )
		return False
