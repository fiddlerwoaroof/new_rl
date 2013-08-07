import numpy as np
import random
import math

class Room(object):
	@property
	def pos(self): return self.x, self.y
	@pos.setter
	def pos(self, v):
		self.x, self.y = v

	@property
	def dim(self): return self.w, self.h
	@dim.setter
	def dim(self, v):
		self.w, self.h = v

	def __init__(self, x,y, w,h, wall_thickness=1):
		'''x,y are coordinates of the top-left corner'''
		self.pos = x,y
		self.dim = w,h
		self.wall_thickness = wall_thickness
		self.door_count = random.randrange(1,min(5,((w+h-2)*2 - 4)))
		self.doors =[]
		self.make_doors()

		if any(d < 2*wall_thickness + 1 for d in (w,h)):
			raise ValueError('no empty space')

	def make_doors(self):
		door_poses = {(0,y) for y in range(self.h)}.union({(y,0) for y in range(self.w)})
		door_poses.update({(self.w-1,y) for y in range(self.h)}.union({(y,self.h-1) for y in range(self.w)}))
		door_poses -= {(x,y) for x in (0,self.w-1) for y in (0,self.h-1)}
		door_poses = list(door_poses)

		for __ in range(self.door_count):
			self.doors.append(random.choice([x for x in door_poses if x not in self.doors]))

	def generate(self):
		room = np.ones(self.dim).astype('int')
		room[self.wall_thickness:-self.wall_thickness,self.wall_thickness:-self.wall_thickness] = 0
		for door in self.doors:
			room[door] = 2
		return room

	def place(self, target):
		room = self.generate()

		print target[self.x:self.x+self.w,self.y:self.y+self.h],'\n', room
		target[self.x:self.x+self.w,self.y:self.y+self.h] = room
		return target

HORIZONTAL = 0
VERTICAL = 1

def minmax(a,b):
	return min(a,b), max(a,b)

class Corridor(object):
	def __init__(self, start, end):
		sx,sy = start
		ex,ey = end
		self.length = abs(sx-ex) + abs(sy-ey)
		self.poses = []

		if ex-sx == 0: self.poses.extend((sx, y) for y in range(sy,ey))
		if ey-sy == 0: self.poses.extend((x, sy) for x in range(sx,ex))
		else:
			meds = []
			curx, cury = start
			motion = True
			while (curx, cury) != end:
				meds.append( (curx,cury) )
				if bool(random.randrange(2)):
					motion = not motion
				tx,ty = curx if motion else ex+1,cury if not motion else ey+1
				curx, cury = self.rand_between( (curx,cury), (tx,ty) )
			for a,b in zip(meds, meds[1:]):
				self.poses.extend(self.fill_line(a,b))

	def place(self, grid, skip_first=False):
		poses = self.poses[1:] if skip_first else self.poses
		for pos in poses:
			grid[pos] = 0
		return grid

	def fill_line(self, a,b):
		#NOTE: only handles horizontal lines.  Should I be using bresenham?
		ax,ay = a
		bx,by = b
		if ax == bx and ay == by:
			yield (ax,ay)
		elif ax == bx:
			x = ax
			miny, maxy = minmax(ay,by)
			for y in range(miny, maxy):
				yield (x,y)
		elif ay == by:
			y = ay
			minx, maxx = minmax(ax,bx)
			for x in range(minx, maxx):
				yield (x,y)
		else:
			raise ValueError('diagonal line')


	def rand_between(self, a, b):
		ax, ay = a
		bx, by = b

		x = ax
		if ax != bx:
			xmin, xmax = minmax(ax,bx)
			if xmax - xmin > 8:
				xmax = xmin + int( (xmax-xmin)/4 )
			x = random.randrange(xmin,xmax)

		y = ay
		if ay != by:
			ymin, ymax = minmax(ay,by)
			if ymax - ymin > 8:
				ymax = ymin + int( (ymax-ymin)/4 )
			y = random.randrange(ymin, ymax)
		return x,y


import unittest
class RoomTest(unittest.TestCase):
	def put_doors(self, room, target):
		for door in room.doors:
			target[door] = 2

	def test_place01(self):
		for __ in range(100):
			room = Room(0,0, 3,3)
			grid = np.ones((3,3), int)
			target = np.array([ [1,1,1], [1,0,1], [1,1,1] ], 'int')
			self.put_doors(room, target)
			np.testing.assert_array_equal(room.place(grid), target)

	def test_place02(self):
		for __ in range(100):
			room = Room(0,0, 4,3)
			grid = np.ones((4,3), int)
			target = np.array([ [1,1,1], [1,0,1], [1,0,1], [1,1,1] ], 'int')
			self.put_doors(room, target)
			np.testing.assert_array_equal(room.place(grid), target)

	def test_generate01(self):
		for __ in range(100):
			room = Room(0,0, 3,3)
			target = np.array([ [1,1,1], [1,0,1], [1,1,1] ], 'int')
			self.put_doors(room, target)
			np.testing.assert_array_equal(room.generate(), target)

	def test_generate02(self):
		for __ in range(100):
			room = Room(0,0, 4,3)
			target = np.array([ [1,1,1], [1,0,1], [1,0,1], [1,1,1] ], 'int')
			self.put_doors(room, target)
			np.testing.assert_array_equal(room.generate(), target)

class Rect(object):
	@property
	def tl(self): return self.lx, self.ty
	@tl.setter
	def tl(self, value): self.lx, self.ty = value

	@property
	def br(self): return self.rx, self.by
	@br.setter
	def br(self, value): self.rx, self.by = value

	@property
	def w(self):
		return self.rx - self.lx

	@property
	def h(self):
		return self.by - self.ty

	def __init__(self, tl, br):
		self.tl = tl
		self.br = br
		# normalize values !!!
		self.normalize()
	def normalize(self):
		self.lx, self.rx = minmax(self.rx, self.lx)
		self.ty, self.by = minmax(self.ty, self.by)

	def get_abs_coord(self, coord):
		x,y = coord
		if x >= 0: x += self.lx
		else: x += self.rx
		if y >= 0: y += self.ty
		else: y += self.by
		return x,y

	def __add__(self, other):
		return Rect(self.tl, other.br)

class Tile(object):
	@property
	def dim(self): return self.w, self.h
	@dim.setter
	def dim(self, v): self.w, self.h = v

	def __init__(self, w,h, num_rooms):
		self.num_rooms = num_rooms
		self.dim = w,h
		if w < 12 or h < 12: raise ValueError('Tile too small')
		self.div_point = random.randrange(5,self.w-4), random.randrange(5,self.h-4)
		# tl, tr, br, bl
		self.sectors = [
			Rect(self.div_point, (0,0)),
			Rect(self.div_point, (self.w,0)),
			Rect(self.div_point, (self.w,self.h)),
			Rect(self.div_point, (0,self.h))
		]

		join_idx = random.randrange(len(self.sectors))
		if num_rooms == 1: self.sectors = [sum(self.sectors, Rect( (0,0), (0,0) ))]
		elif num_rooms == 2:
			group_1 = self.sectors[join_idx], self.sectors[join_idx-1]
			group_2 = [x for x in self.sectors if x not in group_1]
			self.sectors = [group_1[0]+group_1[1], group_2[0]+group_2[1]]
		elif num_rooms == 3:
			group_1 = self.sectors[join_idx], self.sectors[join_idx-1]
			group_2 = [x for x in self.sectors if x not in group_1]
			self.sectors = [group_1[0]+group_1[1]] + list(group_2)

		self.map_items = []
		for x in self.sectors:
			rx,ry = x.get_abs_coord((0,0))
			self.map_items.append(Room(rx,ry, x.w-2, x.h-2))

	def place(self, grid, pos=(0,0)): # NOTE: pos ignored for now
		for item in self.map_items:
			print item.pos, item.dim
			grid = item.place(grid)
		return grid





#class CorridorTest(unittest.TestCase):
	#def put_doors(self, room, target):
		#for door in room.doors:
			#target[door] = 2

	#def test_place01(self):
		#for __ in range(100):
			#room = Room(0,0, 3,3)
			#target = np.array([ [1,1,1], [1,0,1], [1,1,1] ], 'int')
			#self.put_doors(room, target)
			#np.testing.assert_array_equal(room.place(), target)

	#def test_place02(self):
		#for __ in range(100):
			#room = Room(0,0, 4,3)
			#target = np.array([ [1,1,1], [1,0,1], [1,0,1], [1,1,1] ], 'int')
			#self.put_doors(room, target)
			#np.testing.assert_array_equal(room.place(), target)

if __name__ == '__main__':
	unittest.main()