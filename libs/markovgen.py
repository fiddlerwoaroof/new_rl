from __future__ import print_function

import markov
import time
import random
import itertools

chars = itertools.cycle('#,.*')
translator = {x:(' ' if x in 'aeiou' else next(chars)) for x in 'abcdefghijklmnopqrstuvwxyz'}
with open('tmp1') as f:
	combs = []
	for line in f:
		line = line.strip()
		combs.extend(zip(line,line[1:]))

a = markov.MarkovChain( (6,6) )

for l1,l2 in combs:
	l1 = translator[l1]
	l2 = translator[l2]
	a.check_lookup(l1)
	a.check_lookup(l2)
	a.inc_count(l1,l2)

a.calc_prob()

prev = None
x = 0
while x < 10000:
	res = a.get_next(prev)
	print(res, end='')
	prev = res
	x += 1
	if x % 200 == 199: print()
	#time.sleep(0.001)
