import math, sys
from enum import Enum, auto
from Util import Geometry
from Parser import parseChunkData
from abc import ABC

class UnifiedFormat(ABC):
    def __init__(self, coords, level, pos, master):
        self.level = level
        self.coords = Geometry.coord_addition(coords, Geometry.coords_from_index(pos, level=self.level))
        print(f'{(2-self.level)*"    "}{self.coords}')
        self.pos = pos
        self.master = master
        if self.level < 0:
            raise SubdivisionIndexError(self.level)
        
class Point(UnifiedFormat):
    def __init__(self, material, level, coords, pos, master):
        super().__init__(coords, level, pos, master)
        self.material = Material(int(material))
        self.phase = material_phase[self.material]

    def get(self, coords, request):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.pos):
            next_coords = Geometry.coord_mod(coords, 2**self.level)
            try:
                print(coords, self.coords, vars(self)[request])
                return vars(self)[request]
            except KeyError:
                raise InvalidRequestCallError(self.__class__.__name__, request)
        else:
            self.master.get(next_coords)

class Octree(UnifiedFormat):
    def __init__(self, level, coords, pos, master):
        super().__init__(coords, level, pos, master)

        self.contents = []
        self.phase = None

        self.is_create = False
        self.creating_index = 0

    def create_branch(self):
        if self.is_create == True:
            self.contents[self.creating_index].create_branch()
        else:
            self.contents.append(Octree(self.level -1, self.coords, self.creating_index, self))
            self.is_create = True

    def fill_branch(self, material):
        if self.is_create == True:
            self.contents[self.creating_index].fill_branch(material)
        else:
            self.contents.append(Point(material, self.level -1, self.coords, self.creating_index, self))
            self.creating_index += 1

    def close_branch(self):
        if self.is_create == True:
            if self.contents[self.creating_index].close_branch() == True:
                self.creating_index += 1
                self.is_create = False
            return False
        else:
            return True

    def check_phase(self):
        phases = []
        for obj in self.contents:
            phases.append(obj.check_phase())
        self.phase = Phase(int(sum(phases)/len(phases)))
        return self.phase.value

    def get(self, coords, request):
        print(coords, self.coords)
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.pos) and Geometry.coord_compare_less(coords, 0):
            next_coords = Geometry.coord_mod(coords, 2**self.level)
            return self.contents[Geometry.index_from_coords(Geometry.coord_div(next_coords, 2**(self.level-1)))].get(next_coords, request)
        else:
            return self.master.get(coords, request)

class Assembly():
    def __init__(self):
        self.container = []

class Item(Assembly):
    def __init__(self, level, coords=[0, 0, 0], pos=0):
        super().__init__()
        self.octree = Octree(level, coords, pos, self)
        self.phase = Phase.OUT_OF_BOUNDS
        self.level = level

    def grow_octree(self, chunkData):
        parseChunkData(self.octree, chunkData)

    def get(self, coords, request):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.octree.pos) and Geometry.coord_compare_less(coords, 0):
            return self.octree.get(coords, request)
        else:
            try:
                return vars(self)[request]
            except KeyError:
                raise InvalidRequestCallError(self.__class__.__name__, request)

    def check_phase(self):
        self.octree.check_phase()
