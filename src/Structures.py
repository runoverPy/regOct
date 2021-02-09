import math, sys
from enum import Enum, auto
from .Util import *
from .Parser import RegOctLoader as rol
from abc import ABC, abstractmethod

class UnifiedFormat(ABC):
    def __init__(self, coords, level, pos, master, setup):
        if setup == None:
            self.setup = {"default":"0x0"}
        else:
            self.setup = setup
        self.level = level
        self.coords = Geometry.coord_addition(coords, Geometry.coords_from_index(pos, level=self.level))
        self.pos = pos
        self.master = master
        if self.level < 0:
            raise SubdivisionIndexError(self.level)

class Leaf(UnifiedFormat):
    def __init__(self, level, coords, pos, master, data, setup=None):
        super().__init__(coords, level, pos, master, setup)
        for attr in self.setup.items():
            try:
                setattr(self, attr[0], data[attr[1]])
            except KeyError:
                raise UnboundVartagError(attr[1], data)

    def get(self, coords, request):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.pos):
            next_coords = Geometry.coord_mod(coords, 2**self.level)
            try:
                return vars(self)[request]
            except KeyError:
                raise InvalidRequestCallError(self.__class__.__name__, request)
        else:
            self.master.get(next_coords)

class Branch(UnifiedFormat):
    def __init__(self, level, coords, pos, master, setup=None):
        super().__init__(coords, level, pos, master, setup)
        self.contents = []

        self.is_create = False
        self.creating_index = 0

    def create_branch(self, *args):
        if self.is_create == True:
            self.contents[self.creating_index].create_branch()
        else:
            self.contents.append(Branch(self.level -1, self.coords, self.creating_index, self))
            self.is_create = True

    def fill_branch(self, data):
        if self.is_create == True:
            self.contents[self.creating_index].fill_branch(data)
        else:
            self.contents.append(Leaf(self.level -1, self.coords, self.creating_index, self, data))
            self.creating_index += 1

    def close_branch(self, *args):
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

class RegOct():
    def __init__(self, max_level, file_name, setup=None):
        self.octree = Branch(max_level, [0, 0, 0], 0, self)
        self.level = max_level
        self.file_name = file_name

    @classmethod
    def direct(cls, max_level, file_name, setup=None):
        out = cls(max_level, file_name, setup)
        out.load()
        return out

    def get(self, coords, request):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.octree.pos) and Geometry.coord_compare_less(coords, 0):
            return self.octree.get(coords, request)
        else:
            try:
                return vars(self)[request]
            except KeyError:
                raise InvalidRequestCallError(self.__class__.__name__, request)

    def load(self):
        rol(self.octree, self.file_name)

    def print_to_bitmap(self, file_name):
        with open(file_name, "w") as op_fl:
            length = 2**self.octree.level
            op_fl.writelines(["P1\n", f'{length} {length**2}\n'])
            coords = [0, 0, 0]
            for i in range(length):
                coords[0] = i
                for j in range(length):
                    coords[1] = j
                    for k in range(length):
                        coords[2] = k
                        print(f'   --->   {coords}')
                        op_fl.write(f'{str(self.octree.get(coords, "default",))} ')
                    op_fl.write("\n")
                op_fl.write("\n")

def correlate(setup, data):
    for attr in setup.items():
        try:
            print(f'{attr[0]} = {data[attr[1]]}')
        except KeyError:
            raise UnboundVartagError(attr[1], data)

