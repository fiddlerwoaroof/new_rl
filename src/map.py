from __future__ import print_function
import numpy as np
import libtcodpy as tc
import yaml
import libs.bresenham
import libs.cache

def squeeze(val, low, high):
	return min(max(val, low), high)

class TerrainGenBase(object):
	def __init__(self, map):
		self.width, self.height = map.dim
		self.terrain_registry = map.terrain_registry

	def generate(self):
		w,h = self.width, self.height
		terrains, probs = self.terrain_registry.get_terrain_types()
		map = np.random.choice(terrains, (w,h), p=probs)
		chars = np.zeros((w,h)).astype('int')
		fgcolors = np.zeros((w,h,3))
		bgcolors = np.zeros((w,h,3))

		for x, row in enumerate(map):
			for y, cell in enumerate(row):
				char, fgcolor, bgcolor = self.terrain_registry.get_display(cell)
				chars[x,y] = char
				fgcolors[x,y] = fgcolor
				bgcolors[x,y] = bgcolor
		return map, chars, fgcolors, bgcolors

class TerrainGen(TerrainGenBase):
	def generate(self):
		import libs.markov
		import itertools
		w,h = self.width, self.height

		terrains, _ = self.terrain_registry.get_terrain_types()
		terrains = itertools.cycle(terrains)
		translator = {x:terrains.next() for x in 'abcdefghijklmnopqrstuvwxyz'}

		chain = libs.markov.MarkovChain( (200,200) )
		for x in self.terrain_registry.get_terrain_types()[0]:
			chain.check_lookup(str(x))
		with open('data/terraininit') as f:
			combs = []
			for line in f:
				line = line.strip()
				for l1,l2 in zip(line,line[1:]):
					l1 = str(translator[l1])
					l2 = str(translator[l2])
					chain.check_lookup(l1)
					chain.check_lookup(l2)
					chain.inc_count(l1,l2)
		chain.calc_prob()

		map = np.zeros((w,h), int)
		chars = np.zeros((w,h)).astype('int')
		fgcolors = np.zeros((w,h,3))
		bgcolors = np.zeros((w,h,3))

		prev = None
		for x, row in enumerate(map):
			for y, cell in enumerate(row):
				res = chain.get_next(prev)
				char, fgcolor, bgcolor = self.terrain_registry.get_display(int(res))
				if x % 2 == 1:
					y = len(row) - y - 1
				map[x,y] = int(res)
				chars[x,y] = char
				fgcolors[x,y] = fgcolor
				bgcolors[x,y] = bgcolor
				prev = res
		return map, chars, fgcolors, bgcolors



class Map(object):
	def __init__(self, w, h, terrain_registry):
		self.pov = None
		self.povcache = libs.cache.Cache()

		self.width = w
		self.height = h
		self.terrain_registry = terrain_registry
		self.overlays = {} # (x,y): { set( object, ... ) }

		self.ids, self.map, self.fgcolors, self.bgcolors = TerrainGen(self).generate()

		self.fov = FovCache(self, self.terrain_registry)

	def add(self, object):
		self.overlays.setdefault(object.pos,[]).append(object)

	def check_and_execute_bump(self, object, x,y):
		if (x,y) in self.overlays:
			for other in self.overlays[x,y]:
				object.bump(other)

	def interact(self, a, bs):
		#print 'interacting with:', bs
		for b in bs:
			a.interact(b)

	def remove(self, object):
		pos = object.pos
		if pos in self.overlays and object in self.overlays[pos]:
			self.overlays[pos].remove(object)

	def move(self, object, dx,dy, update_cb):
		ox,oy = object.pos

		if abs(dx) < 2 and abs(dy) < 2:
			self.overlays[object.pos].remove(object)

			collide_x, collide_y = None, None
			x = squeeze(ox+dx, 0, self.width-1)
			y = squeeze(oy+dy, 0, self.height-1)
			if not self.is_passable((x,y)):
				collide_x, collide_y = x,y
				x,y = ox,oy
			update_cb(x-ox, y-oy)

			if collide_x is not None:
				self.check_and_execute_bump(object, collide_x, collide_y)
			if object.pos in self.overlays:
				self.interact(object, self.overlays[object.pos])

			self.overlays.setdefault((x,y), []).append(object)
			self.update_overlay(ox,oy)
		else:
			# calculate the deltas for each step
			line = list(libs.bresenham.line(0,0, dx,dy, 0))
			line = [(bx-ax, by-ay) for (ax,ay), (bx,by) in zip(line,line[1:])]
			#print line
			for x,y in line:
				if self.move(object, x,y, update_cb) != (x,y):
					break
			x,y = object.pos

		return x-ox, y-oy

	def move_toward_origin(self, object, update_cb):
		if self.pov is None: raise ValueError('No origin set')
		term, _ = self.pov
		dx,dy = self.fov.get_pathstep(object.pos, term)
		return self.move(object, dx,dy, update_cb)

	def update_overlay(self, x=None, y=None):
		if x is None or y is None: pass
		else:
			if (x,y) in self.overlays and self.overlays[x,y] == []:
				self.overlays.pop((x,y))

	def set_pov(self, pov):
		self.pov = pov

	def get_visible_objects(self):
		o,r = self.pov
		results = set()
		for x,y in self.overlays:
			if self.fov.is_visible(o,r, (x,y)):
				results.update(self.overlays[x,y])
		return results



	def get_rgb(self, colors, fg=True,slices=(slice(0),slice(0))):
		result = np.rollaxis(colors, 2)
		return [x.transpose() for x in result]

	def draw(self, con, tl=(0,0)):
		def mv(x,y, (lx,ty)):
			return x-lx, y-ty
		br = tl[0]+con.width, tl[1]+con.height
		slices = slice(tl[0], br[0]), slice(tl[1], br[1])

		fgcolors = self.fgcolors.astype('int')
		bgcolors = self.bgcolors.astype('int')
		color_mask = np.ones( (con.width, con.height, 3) )
		char_mask = np.ones( (con.width, con.height) ).astype('bool')

		if self.pov is not None:
			origin, radius = self.pov
			ox, oy = origin
			if ox+radius >= br[0] or oy+radius >= br[1]:
				xmod, ymod = 0,0
				if ox + radius >= br[0]:
					xmod = min(ox + radius - br[0], self.width - br[0])
				if oy + radius >= br[1]:
					ymod =  min(oy + radius - br[1], self.height - br[1])
				br = br[0] + xmod, br[1] + ymod
				tl = tl[0] + xmod, tl[1] + ymod
				slices = slice(tl[0], br[0]), slice(tl[1], br[1])
			def calc_mask():
				for x in range(tl[0], br[0]):
					for y in range(tl[1], br[1]):
						if not self.fov.is_visible(origin, radius, (x,y)):
							color_mask[x-tl[0], y-tl[1]] = (0.25, 0.5, 0.5)
							char_mask[x-tl[0], y-tl[1]] = False
				return color_mask, char_mask
			color_mask, char_mask = self.povcache.get( (origin,radius,tl), calc_mask )
			fgcolors = (fgcolors[slices] * color_mask).astype('int')
			bgcolors = (bgcolors[slices] * color_mask).astype('int')
		else:
			fgcolors = fgcolors[slices]
			bgcolors = bgcolors[slices]

		tc.console_fill_foreground(con.con, *self.get_rgb(fgcolors))
		tc.console_fill_background(con.con, *self.get_rgb(bgcolors, False))

		chars = np.copy(self.map[slices])
		for x,y in self.overlays:
			screen_x = x-tl[0]
			screen_y = y-tl[1]
			if (not (tl[0] <= x < br[0])) or (not (tl[1] <= y < br[1])): continue
			elif not char_mask[screen_x,screen_y]: continue
			if 0 <= screen_x < con.width and 0 <= screen_y < con.height:
				obj = self.overlays[x,y][-1]
				chars[screen_x,screen_y] = obj.char
				tc.console_set_char_background(con.con, screen_x,screen_y, tc.Color(*bgcolors[screen_x,screen_y]))
				tc.console_set_char_foreground(con.con, screen_x,screen_y, tc.Color(*obj.color))
		chars[np.logical_not(char_mask)] = ord(' ')
		tc.console_fill_char(con.con, chars.transpose())

	def coord_iter(self):
		return ( (x,y) for x in range(self.width) for y in range(self.height) )

	@property
	def dim(self):
		return self.width, self.height

	def is_visible(self, coord):
		result = True
		if self.pov is not None:
			o,r = self.pov
			result = self.fov.is_visible(o,r, coord)
		return result

	def is_passable(self, coord):
		if coord in self.overlays and any(x.blocks for x in self.overlays[coord]):
			return False
		else:
			return self.fov.is_passable(coord)


class FovCache(object):
	# TODO: get allow updates to base_map
	def __init__(self, map, terrain_registry):
		self.width, self.height = map.dim

		self.base_map = tc.map_new(*map.dim)

		for x,y in map.coord_iter():
			if (x,y) in map.overlays:
				object = map.overlays[x,y]
				pssble,trnsprnt = object.passable, object.transparent
			else:
				pssble,trnsprnt = terrain_registry.get_props(map.ids[x,y])
			tc.map_set_properties(self.base_map, x,y, trnsprnt,pssble)

		self.fovmaps = {}
		self.paths   = {}

	def get_fovmap(self, origin, radius):
		key = origin,radius

		if key in self.fovmaps: fovmap = self.fovmaps[key]
		else:
			fovmap = tc.map_new(self.width, self.height)
			tc.map_copy(self.base_map, fovmap)
			self.fovmaps[key] = fovmap

			x,y = origin
			tc.map_compute_fov(fovmap, x,y, radius, algo=tc.FOV_DIAMOND)

		return fovmap

	def get_pathmap(self, term):
		'''note: running libtcod's functions backwards, since the player's position is more stable than the AI's'''
		key = term
		if key not in self.paths:
			tx,ty = term
			pmap = self.paths[key] = tc.dijkstra_new(self.base_map, 1)
			tc.dijkstra_compute(pmap, tx,ty)
		return self.paths[key]

	def get_pathstep(self, origin, term):
		ox,oy = origin
		pmap = self.get_pathmap(term)
		dx,dy = 0,0 # don't move if no path
		if tc.dijkstra_path_set(pmap, ox,oy): # NOTE: walk path backwards!!!
			plen = tc.dijkstra_size(pmap)
			x,y = tc.dijkstra_get(pmap, plen-2)
			dx,dy = x-ox, y-oy
		#print 'dijkstra step: %d,%d' % (dx,dy)
		return dx,dy



	def is_visible(self, origin, radius, coord):
		fovmap = self.get_fovmap(origin, radius)
		return tc.map_is_in_fov(fovmap, *coord)

	def is_transparent(self, coord):
		return tc.map_is_transparent(self.base_map, *coord)
	def is_passable(self, coord):
		return tc.map_is_walkable(self.base_map, *coord)


class TerrainInfo(object):
	passable = False
	transparent = False
	char = ord(' ')
	fg = (255,255,255)
	bg = (0,0,0)
	prob = 1

	@classmethod
	def make_terrain(cls, name, char, passable, transparent,fg,bg, prob=1):
		if hasattr(char, 'upper'): char = ord(char)
		passable = bool(passable)
		transparent = bool(transparent)
		return type(name, (cls,), dict(char=char, passable=passable, transparent=transparent,fg=fg,bg=bg,prob=prob))

import patches.yaml_omap_patch
class TerrainRegistry(object):
	def __init__(self):
		self.id = 0
		self.registry = {}
		self.names = {}
		self.types = {}

	def get_terrain(self, id):
		ter = self.registry[id]
		return ter

	def get_props(self, id):
		ter = self.get_terrain(id)
		return ter.passable, ter.transparent

	def get_display(self, char):
		ter = self.get_terrain(char)
		return ter.char, ter.fg, ter.bg

	def get_terrain_types(self):
		types, probabilities = zip(*[(x, self.registry[x].prob) for x in self.registry])
		probs = [float(x) / sum(probabilities) for x in probabilities]
		return types, probs


	def register(self, ter, classes):
		self.id += 1
		self.registry[self.id] = ter
		self.names[ter.__name__] = ter
		for klass in classes:
			self.types.setdefault(klass, []).append(ter)
		return ter

	def new_terrain(self, name, char, passable=False, transparent=False, fg=(255,255,255), bg=(0,0,0), prob=1, classes=('open',)):
		ter = TerrainInfo.make_terrain(name, char, passable, transparent, fg,bg, prob=prob)

		classes = set(classes)
		if not passable: classes.add('blocks_movement')
		if not transparent: classes.add('blocks_sight')

		return self.register(ter, classes)

	def load_from_file(self, fn, loader=yaml.load):
		with open(fn) as f:
			values = loader(f)
		for name, terrain in values.viewitems():
			self.new_terrain(name, **terrain)


