import libs.patch_random
import random
random.seed(2)

import libtcodpy as tc
import numpy as np

from libs import overlay
from libs import combat
from src import events
from src import player
from src import console
from src import map

import random


class Application(object):
	def __init__(self):
		self.screen = console.Screen(100,63)
		self.terrain_registry = map.TerrainRegistry()
		self.terrain_registry.load_from_file('data/terrain.yml')
		self.map = map.Map(100,63, self.terrain_registry)
		self.player = player.Player(4,5, self.map, combat.Adventurer.randomize())
		self.events = events.EventHandler()
		player.ArrowHandler(self.player, self.events)

		self.actors = []
		for x in range(40):
			self.actors.append(overlay.Actor(random.randrange(100), random.randrange(63), self.map))

		self.objects = []
		for x in range(50):
			self.objects.append(overlay.Potion(random.randrange(100), random.randrange(63), self.map))

		tc.sys_set_fps(60)

	def init(self):
		self.screen.init("test")
		self.player.draw()
		for actor in self.actors:
			actor.draw()

	def run(self):
		while not tc.console_is_window_closed():
			self.events.tick()
			self.map.draw(self.screen)
			tc.console_print(0, 0,1, '%d' % tc.sys_get_fps())
			tc.console_flush()


if __name__ == '__main__':
	app = Application()
	app.init()
	app.run()
