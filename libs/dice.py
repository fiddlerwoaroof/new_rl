import random
import collections
import itertools
import re

basestr = (str,unicode)

class DieJar(object):
	parser = re.compile(r'^(?:_?(?P<num>[1-9][0-9]*))?d(?P<sides>[1-9][0-9]*)$')
	def __getattr__(self, key):
		out = []
		for sect in key.split('__'):
			out.extend(self.parse_section(sect))
		return Dice(out)

	def parse_section(self, key):
		out = self.parser.match(key)
		if out is None:
			raise AttributeError('invalid die specification')
		else:
			dct = out.groupdict()
			dct['sides'] = int(dct['sides'])
			dct['num'] = int(dct['num'] or 1)
			dice = [Die(dct['sides']) for __ in range(dct['num'])]
			return dice





def iterable(obj):
	return (not isinstance(obj, basestr)) and isinstance(obj, collections.Iterable)

def flatten(lis):
	return itertools.chain(*[(x if iterable(x) else [x]) for x in lis])

class Die(object):
	'Note: hashed by sides, min and step.  Consequently not necessarily preserved when used as a dictionary key'
	def __init__(self, sides, min=1, step=1):
		self.sides = sides
		self.min = min
		self.step = 1
		self.sides = sides
		self.choices = range(min, (min+sides)*step, step)
		self._value = None
		self.combine_func = lambda a,b: a+b

	def roll(self):
		self._value = random.choice(self.choices)
		return self._value

	@property
	def value(self):
		if self._value is None: self.roll()
		return self._value

	def combine(self, other):
		if hasattr(other, 'value'): other = other.value
		return self.combine_func(self.value, other.value)

	def __str__(self):
		base = 'd%d' % self.sides
		if self.min != 1:
			base = '%s+%d' % (base,self.min)
		if self.step != 1:
			base = '(%s)*%d' % (base, self.step)
		return base

	def __eq__(self, other):
		return (self.sides == other.sides) and (self.min == other.min) and (self.step == other.step)

	def __hash__(self):
		return hash((self.sides,self.min,self.step))

class Dice(collections.Sequence):
	'A collection of dice, can be initialized either with Die instances or lists of Die instances'

	def __init__(self, *dice, **kw):
		self.dice = list(flatten(dice))
		self.combiner = kw.get('combiner', lambda a,b:a+b)

	def __getitem__(self, k): return self.dice[k]
	def __len__(self): return len(self.dice)

	def roll(self):
		return reduce(self.combiner, (die.roll() for die in self.dice))
	def __str__(self):
		groups = collections.Counter(self.dice)
		out = []
		dice = sorted(groups, key=lambda k:-groups[k])
		if len(dice) > 1:
			for die in dice[:-1]:
				count = groups[die]
				out.append('%d%s' % (count,die))
			out = ','.join(out)
			out = ' and '.join([out, str(dice[-1])])
		else:
			out = '%d%s' % (groups[dice[0]],dice[0])


		return out



MULT=1
ADD=2
class DieRoll(object):
	def __init__(self, dice=None, adjustments=None):
		self.dice = dice
		self.adjustments = [] if adjustments is None else adjustments

	def add_adjustment(self, add=None, mult=None):
		if None not in {add,mult}: raise ValueError('can\'t add two adjustments at once')
		elif {add,mult} - {None} == set(): raise ValueError('No adjustment given')

		if add is not None:
			adjustment = (ADD,add)
		elif mult is not None:
			adjustment = (MULT,mult)
		self.adjustments.append(adjustment)

	def roll(self):
		result = self.dice.roll()
		for type,bonus in self.adjustments:
			if type == MULT:
				result *= type
			elif type == ADD:
				result += bonus
		return result

if __name__ == '__main__':
	import unittest
	tests = unittest.TestSuite()
	inst = lambda a:a()

	class TestDie(unittest.TestCase):
		def test_roll_plain(self):
			a = Die(6)
			for __ in range(40):
				self.assertLess(a.roll(), 7)
				self.assertGreater(a.roll(), 0)
		def test_roll_min(self):
			a = Die(6,min=4)
			for __ in range(40):
				self.assertLess(a.roll(), 6+4+1)
				self.assertGreater(a.roll(), 3)
		def test_roll_step(self):
			a = Die(6,step=2)
			for __ in range(40):
				self.assertLess(a.roll(), 6+(6*2)+1)
				self.assertGreater(a.roll(), 0)
				self.assertTrue((a.roll()-1) % 2 == 0)
		def test_str(self):
			self.assertEqual(str(Die(6)), 'd6')
			self.assertEqual(str(Die(6,min=2)), 'd6+2')

	class TestDice(unittest.TestCase):
		def test_init(self):
			dice = [Die(6) for __ in range(20)]
			a = Dice(dice)
			self.assertEqual(dice,a.dice)
			a = Dice(*dice)
			self.assertEqual(dice,a.dice)
		def test_roll(self):
			dice = [Die(6) for __ in range(2)]
			dice = Dice(dice)
			self.assertGreater(dice.roll(), 1)
			self.assertLess(dice.roll(), 13)

	class TestDieRoll(unittest.TestCase):
		pass

	unittest.main()
