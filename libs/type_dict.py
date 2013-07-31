import collections
import copy

class TypeDict(collections.MutableMapping):
	def __init__(self, *args, **kw):
		if '__default' in kw:
			self.default = kw.pop('__default')

		self.store = dict(args)
		self.store.update(kw)

	def get_store(self, cls):
		cur = self.store
		bases = cls.__bases__
		if bases:
			head, tail = bases[0], bases[1:]
			while tail:
				cur = self.store.setdefault(head, {})
				head, tail = tail[0], tail[1:]
		return cur

	def __getitem__(self, cls):
		store = self.get_store(cls)
		try:
			print store
			return store[cls]
		except KeyError:
			if hasattr(self, 'default'):
				return copy.copy(self.default)
			else:
				raise

	def __setitem__(self, cls, value):
		store = self.get_store(cls)
		store[cls] = value
	def __delitem__(self, cls):
		store = self.get_store(cls)
		del store[cls]

	def __iter__(self):
		return TypeDictIterator(self)
	def __len__(self):
		return len(self.slots)

class _Null: pass

class TypeDictIterator(collections.Iterator):
	def __init__(self, dct):
		self.dct = dct
		self.dcts = [dct]
		self.iters = [iter(dct)]
		self.cur = self.iters[-1]

	def next(self):
		result = _Null
		try: result = self.cur.next()
		except StopIteration:
			self.iters.pop()
			self.dcts.pop()
			if self.iters:
				self.cur = self.iters[-1]
				result = self.cur.next()
			else:
				raise StopIteration

		if result in self.dcts[-1] and self.dcts[-1][result]:
			self.iters.append(iter(self.dcts[-1][result]))
			self.cur = self.iters[-1]

		return result


