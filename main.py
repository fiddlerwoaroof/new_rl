import libs.patch_random
import random
#random.seed(2)

import libtcodpy as tc
import numpy as np

from libs import overlay
from libs import combat
from src import events
from src import player
from src import console
from src import map

import random
import bisect


WIDTH = 79
HEIGHT = 46
class Application(object):
	def __init__(self):
		self.screen = console.Screen(WIDTH, HEIGHT)
		self.terrain_registry = map.TerrainRegistry()
		self.terrain_registry.load_from_file('data/terrain.yml')
		self.map = map.Map(WIDTH,HEIGHT, self.terrain_registry)
		self.player = player.Player(4,5, self.map, combat.Adventurer.randomize())
		self.events = events.EventHandler()
		player.ArrowHandler(self.player, self.events)

		self.actors = []
		for x in range(40):
			self.actors.append(overlay.Actor(random.randrange(WIDTH), random.randrange(HEIGHT), self.map))

		self.objects = []
		for x in range(50):
			self.objects.append(overlay.Potion(random.randrange(WIDTH), random.randrange(HEIGHT), self.map))

		tc.sys_set_fps(60)

	def update_actors(self):
		to_pop = []
		for idx,actor in enumerate(self.actors):
			if not actor.tick():
				bisect.insort(to_pop, idx)
		for pop in reversed(to_pop):
			self.actors.pop(pop)

	def init(self):
		self.screen.init("test")
		self.player.draw()
		self.update_actors()
		for overlay in self.actors + self.objects:
			overlay.draw()

	def run(self):
		while not tc.console_is_window_closed():
			self.events.tick()
			self.update_actors()
			self.map.draw(self.screen)
			tc.console_print(0, 0,1, '%d' % tc.sys_get_fps())
			tc.console_flush()


if __name__ == '__main__':
	app = Application()
	app.init()
	app.run()
