if __name__ == '__main__':
    execfile('/home/edwlan/python_envs/roguelike/bin/activate_this.py',  dict(__file__='/home/edwlan/python_envs/roguelike/bin/activate_this.py'))

import libs.patch_random
import random
#random.seed(2)

import libtcodpy as tc
import numpy as np

from gui import text_display
from libs import overlay
from libs import combat
from src import events
from src import player
from src import console
from src import map

import random
import bisect

from twisted.internet import reactor
import twisted.internet


WIDTH = 118
HEIGHT = 62
class Application(object):
	def __init__(self):
		self.screen = console.Screen(WIDTH, HEIGHT+5)
		self.console = console.Console(WIDTH, HEIGHT, self.screen)
		self.message_console = console.Console(WIDTH, 5, self.screen, (0,HEIGHT))
		self.messages = text_display.MessageBox(self.message_console, 5, (10,0), 'msg')
		self.fps_display = text_display.Label(self.message_console, (0,0), None)

		self.terrain_registry = map.TerrainRegistry()
		self.terrain_registry.load_from_file('data/terrain.yml')
		self.map = map.Map(200,200, self.terrain_registry)
		self.tc_events = events.TCODEventHandler()
		self.events = events.EventHandler()

		self.player = player.Player(4,5, self.map, combat.Adventurer.randomize())
		self.player_stat = text_display.TextBox(self.message_console, 4, (0,1))
		self.player.claim_display(self.player_stat)
		player.ArrowHandler(self.player, self.tc_events)

		self.actors = [self.player]
		for x in range(40):
			self.actors.append(overlay.AIActor(random.randrange(WIDTH), random.randrange(HEIGHT), self.map))
		self.player.register_event('update', self.tick_actors)

		self.objects = []
		for x in range(50):
			self.objects.append(overlay.Potion(random.randrange(WIDTH), random.randrange(HEIGHT), self.map))

		tc.sys_set_fps(30)

	def tick_actor(self, actor):
		keep = actor.tick()
		if not keep:
			self.actors.remove(actor)
			self.objects.append(actor)

	def update_actors(self):
		self.player.tick()

	def tick_actors(self, player):
		print 'actor_tick'
		to_pop = []
		for idx,actor in enumerate(self.actors[1:],1):
			if not actor.tick():
				bisect.insort(to_pop, idx)
		for pop in reversed(to_pop):
			actor = self.actors.pop(pop)
			self.objects.append(actor)

	def init(self):
		self.screen.init("test")
		self.message_console.fill(0,0,128)
		#self.player.draw()
		for overlay in self.actors + self.objects:
			overlay.draw()

	def tick(self):
		self.tc_events.tick()
		self.fps_display.set_text('%d', tc.sys_get_fps())
		self.update_actors()
		self.map.draw(self.console)
		self.console.blit()
		self.message_console.blit()
		tc.console_flush()
		if tc.console_is_window_closed():
			reactor.stop()
		else:
			reactor.callLater(0, self.tick)


if __name__ == '__main__':
	app = Application()
	app.init()
	reactor.callWhenRunning(app.tick)
	reactor.run()
