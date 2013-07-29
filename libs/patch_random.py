# Copyright (c) 2011 Edward Langley
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# Neither the name of the project's author nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 

import random
import numpy.random

class MyRand(random.Random):
  def random(self):
    return numpy.random.random()
  def seed(self, a=None):
    if a is None:
      import time
      a = time.time() * 10000
    print a
    numpy.random.seed(int(a))
    self.gauss_next = None
  def setstate(self, state):
    numpy.random.set_state(state)
  def getstate(self):
    return numpy.random.get_state()
  def jumpahead(self, n):
    self.seed()

_inst = random._inst = MyRand()
random.seed = _inst.seed
random.random = _inst.random
random.uniform = _inst.uniform
random.triangular = _inst.triangular
random.randint = _inst.randint
random.choice = _inst.choice
random.randrange = _inst.randrange
random.sample = _inst.sample
random.shuffle = _inst.shuffle
random.normalvariate = _inst.normalvariate
random.lognormvariate = _inst.lognormvariate
random.expovariate = _inst.expovariate
random.vonmisesvariate = _inst.vonmisesvariate
random.gammavariate = _inst.gammavariate
random.gauss = _inst.gauss
random.betavariate = _inst.betavariate
random.paretovariate = _inst.paretovariate
random.weibullvariate = _inst.weibullvariate
random.getstate = _inst.getstate
random.setstate = _inst.setstate
random.jumpahead = _inst.jumpahead
random.getrandbits = _inst.getrandbits

