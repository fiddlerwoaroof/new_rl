import numpy as np
import libtcodpy as tc
import yaml
import libs.bresenham

def squeeze(val, low, high):
	return min(max(val, low), high)

class TerrainGen(object):
	def __init__(self, map):
		self.width, self.height = map.dim
		self.terrain_registry = map.terrain_registry

	def generate(self):
		w,h = self.width, self.height
		terrains, probs = self.terrain_registry.get_terrain_types()
		print terrains, probs
		map = np.random.choice(terrains, (w,h), p=probs)
		print map[map>4]
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


class Map(object):
	def __init__(self, w, h, terrain_registry):
		self.pov = None
		self.width = w
		self.height = h
		self.terrain_registry = terrain_registry
		self.overlays = {} # (x,y): { set( object, ... ) }

		self.ids, self.map, self.fgcolors, self.bgcolors = TerrainGen(self).generate()

		self.fov = FovCache(self, self.terrain_registry)

	def add(self, object):
		self.overlays.setdefault(object.pos,[]).append(object)

	def move(self, object, dx,dy):
		print self.overlays,
		self.overlays[object.pos].remove(object)

		if abs(dx) < 2 and abs(dy) < 2:
			ox,oy = object.pos
			x = squeeze(ox+dx, 0, self.width-1)
			y = squeeze(oy+dy, 0, self.height-1)
			if not self.fov.is_passable((x,y)):
				x,y = ox,oy

		else:
			ox,oy = object.pos
			tx,ty = ox+dx, oy+dy
			gx,gy = ox,oy
			for x,y in libs.bresenham.line(ox,oy, tx,ty, 1):
				if not self.fov.is_passable((x,y)): break
				else: gx,gy = x,y
			x,y = gx,gy

		self.overlays.setdefault((x,y), []).append(object)
		self.update_overlay(ox,oy)
		return x-ox, y-oy

	def update_overlay(self, x=None, y=None):
		if x is None or y is None: pass
		else:
			if (x,y) in self.overlays and self.overlays[x,y] == []:
				self.overlays.pop((x,y))

	def get_rgb(self, fg=True,slices=(slice(0),slice(0))):
		if fg:
			result = np.rollaxis(self.fgcolors[slices], 2)
		else:
			result = np.rollaxis(self.bgcolors[slices], 2)
		return [x.transpose() for x in result]

	def draw(self, con, tl=(0,0)):
		br = tl[0]+con.width, tl[1]+con.height
		slices = slice(tl[0], tl[0]+con.width), slice(tl[1], tl[1]+con.height)
		tc.console_fill_foreground(con.con, *self.get_rgb(slices=slices))
		tc.console_fill_background(con.con, *self.get_rgb(False,slices=slices))

		chars = np.copy(self.map[slices])
		for x,y in self.overlays:
			screen_x = x-tl[0]
			screen_y = y-tl[1]
			if 0 <= screen_x < con.width and 0 <= screen_y < con.height:
				obj = self.overlays[x,y][-1]
				chars[screen_x,screen_y] = obj.char
				tc.console_set_char_foreground(con.con, screen_x,screen_y, tc.black)
				tc.console_set_char_background(con.con, screen_x,screen_y, tc.white)
		tc.console_fill_char(con.con, chars.transpose())

	def coord_iter(self):
		return ( (x,y) for x in range(self.width) for y in range(self.height) )

	@property
	def dim(self):
		return self.width, self.height


class FovCache(object):
	# TODO: get allow updates to base_map
	def __init__(self, map, terrain_registry):
		self.base_map = tc.map_new(*map.dim)

		for x,y in map.coord_iter():
			if (x,y) in map.overlays:
				object = map.overlays[x,y]
				pssble,trnsprnt = object.passable, object.transparent
			else:
				pssble,trnsprnt = terrain_registry.get_props(map.ids[x,y])
			tc.map_set_properties(self.base_map, x,y, trnsprnt,pssble)

		self.fovmaps = {}

	def get_fovmap(self, terrain_registry, origin, radius):
		key = origin,radius

		if key in self.fovmaps: fovmap = self.fovmaps[key]
		else:
			fovmap = tc.map_new(self.width, self.height)
			tc.map_copy(self.base_map, fovmap)
			self.fovmaps[key] = fovmap

			x,y = origin
			tc.map_compute_fov(fovmap, x,y, radius)

		return fovmap

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

class TerrainRegistry(object):
	def __init__(self):
		self.id = 0
		self.registry = {}
		self.names = {}

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


	def register(self, ter):
		self.id += 1
		self.registry[self.id] = ter
		self.names[ter.__name__] = ter
		return ter

	def new_terrain(self, name, char,
		passable=False, transparent=False, fg=(255,255,255), bg=(0,0,0), prob=1
	):
		print 'prob: %f' % prob
		ter = TerrainInfo.make_terrain(name, char, passable, transparent, fg,bg, prob=prob)
		return self.register(ter)

	def load_from_file(self, fn, loader=yaml.safe_load):
		with open(fn) as f:
			values = loader(f)
		for name, terrain in values.viewitems():
			self.new_terrain(name, **terrain)


