import math, sys
from enum import Enum, auto
from Util import *
from Parser import RegOctLoader as rol
from abc import ABC, abstractmethod

class UnifiedFormat(ABC):
    def __init__(self, coords, level, pos, master):
        self.level = level
        self.coords = Geometry.coord_addition(coords, Geometry.coords_from_index(pos, level=self.level))
        self.pos = pos
        self.master = master
        if self.level < 0:
            raise SubdivisionIndexError(self.level)
        
class Point(UnifiedFormat):
    def __init__(self, material, level, coords, pos, master):
        super().__init__(coords, level, pos, master)

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

    def get(self, coords, request):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.pos) and Geometry.coord_compare_less(coords, 0):
            next_coords = Geometry.coord_mod(coords, 2**self.level)
            return self.contents[Geometry.index_from_coords(Geometry.coord_div(next_coords, 2**(self.level-1)))].get(next_coords, request)
        else:
            return self.master.get(coords, request)

class Box:
    def __init__(self, max_level, file_name):
        self.octree = Octree(max_level, [0, 0, 0], 0, self)
        self.level = max_level
        self.file_name = file_name
        rol(self.octree, self.file_name)

    def get(self, coords, request):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.octree.pos) and Geometry.coord_compare_less(coords, 0):
            return self.octree.get(coords, request)
        else:
            try:
                return vars(self)[request]
            except KeyError:
                raise InvalidRequestCallError(self.__class__.__name__, request)

def correlate(setup, data):
    for attr in setup.items():
        try:
            print(f'{attr[0]} = {data[attr[1]]}')
        except KeyError:
            raise UnboundVartagError(attr[1], data)

if __name__ == "__main__":
    setup = {"python_is_awesome":"0x0", "trollfaces":"0x1", "spanish_inquisition":"0x2", "intentionally_missing":"0x3"}
    data = {"0x0":True, "0x2":"unexpected", "0x1":1}
    correlate(setup, data)