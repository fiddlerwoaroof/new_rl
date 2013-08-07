# vim: set fileencoding=utf-8 :
from __future__ import print_function
import time

import numpy
import pickle
import yaml
import os
import bz2

class MarkovChain(object):
	def __init__(self, size):
		self.counts = numpy.matrix(numpy.zeros(size))
		self.probs = numpy.matrix(numpy.zeros(size))
		self.lookup = {'EOF':0}
		self.__lookup_key = 1

	def add_lookup(self, l):
		self.lookup[l] = self.__lookup_key
		self.__lookup_key += 1

	def check_lookup(self, l):
		if l not in self.lookup:
			self.add_lookup(l)

	def get_keys(self, a,b):
		a = self.lookup[a]
		b = self.lookup[b]
		return a,b

	def inc_count(self, a,b, times=1):
		a,b = self.get_keys(a,b)
		self.counts[a,b] += times

	def calc_prob(self):
		for idx, row in enumerate(self.counts):
			if row.sum() != 0:
				self.probs[idx] = row / row.sum()
		return self.probs

	def get_prob(self, l1,l2=None):
		l1 = self.lookup[l1]
		if l2 is None:
			result = numpy.array(self.probs)[l1][:max(self.lookup.values())+1]
		else:
			l2 = self.lookup[l2]
			result = self.probs[l1,l2]
		return result

	@classmethod
	def from_yml(cls, fil, bzip2=True):
		self = object.__new__(cls)
		d = fil.read()
		if bzip2:
			d = bz2.decompress(d)
		d = yaml.load(d)
		self.lookup = d['key']
		self.probs = d['data']
		self.counts = d['counts']
		return self

	def to_yml(self, fil):
		yaml.dump({'data':self.probs, 'key':self.lookup, 'counts':self.counts}, fil)

	def get_next(self, prev=None):
		if prev is None:
			prev = numpy.random.choice(list(self.lookup.keys()))
		choices = sorted(self.lookup.keys(), key=lambda x:self.lookup[x])
		probabilities = self.get_prob(prev)
		return numpy.random.choice(choices, p=probabilities)

	def new_word(self):
		word = [numpy.random.choice(list(x for x in self.lookup if x.isupper() and x != 'EOF'))]
		while len(word)-1 <= 3 or word[-1] != 'EOF':
			if word[-1] == 'EOF': word.pop()
			elif len(word) > 8 and self.get_prob(word[-1], 'EOF') > 0.01: break
			next = self.get_next(word[-1])
			if len(word) > 1 and next == word[-1] == word[-2]: continue
			else: word.append(next)
		word.pop()
		return ''.join(word)

if __name__ == '__main__':
	if os.path.exists('markov.yml.bz2'):
		with open('markov.yml.bz2', 'rb') as f:
			a = MarkovChain.from_yml(f)
	elif os.path.exists('markov.yml'):
		with open('markov.yml', 'rb') as f:
			a = MarkovChain.from_yml(f, False)
	else:
		a = MarkovChain((200,200))
		with open('llnames') as f:
			for l in f:
				l = l.strip()
				count, word = l.split()
				count = int(count)
				word = list(word)
				word.append('EOF')
				for ___ in range(count):
					for l1,l2 in zip(word,word[1:]):
						a.check_lookup(l1)
						a.check_lookup(l2)
						a.inc_count(l1,l2)

		a.calc_prob()

		with open('markov.yml', 'w') as f:
			a.to_yml(f)

		print('dumped')


	import unicodedata
	import unidecode

	out = set()
	while len(out) < 1000:
		res = a.new_word()
		if res not in out:
			print(res, '=', unidecode.unidecode(res))
			out.add(res)
		time.sleep(0.1)

