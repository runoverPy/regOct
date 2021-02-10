import math, sys, time
from enum import Enum, auto
from .Util import *
from .Reader import Reader
from abc import ABC, abstractmethod
import warnings

class UnifiedFormat(ABC):
    def __init__(self, coords, level, pos, master):
        self.setup = master.setup
        self.level = level
        self.coords = Geometry.coord_addition(coords, Geometry.coords_from_index(pos, level=self.level))
        self.pos = pos
        self.master = master
        if self.level < 0:
            raise SubdivisionIndexError(self.level)

    def leaf_attributes(self, data):
        for attr in self.setup.items():
            try:
                setattr(self, attr[0], data[attr[1]])
            except KeyError:
                raise UnboundVartagError(attr[1], data)

    def implicit_attributes(self):
        pass

    def default_attributes(self):
        pass

    def collect_implicits(self):
        pass
    
    def header(self, data):
        if data["0x0"] != "0.0.2":
            warnings.warn("The ONC version of the file has been outdated.")
            if (output := input("UPDATE FILE: (y/n)\n"))[0] == "y":
                print("its definitely updating rn")
            elif output[0] == "n":
                print("your loss")
                time.sleep(1)
                raise ToasterBathError()

class Leaf(UnifiedFormat):
    def __init__(self, level, coords, pos, master, data, setup=None):
        super().__init__(coords, level, pos, master)
        super().leaf_attributes(data)

    def get(self, coords, *requests):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.pos):
            next_coords = Geometry.coord_mod(coords, 2**self.level)
            try:
                output = {}
                for request in requests:
                    output[request] = vars(self)[request]
                return output
            except KeyError:
                raise InvalidRequestCallError(self.__class__.__name__, requests)
        else:
            self.master.get(next_coords, *requests)

class Branch(UnifiedFormat):
    def __init__(self, level, coords, pos, master):
        super().__init__(coords, level, pos, master)
        self.contents = []

        self.is_create = False
        self.creating_index = 0

    def create_branch(self, args):
        if self.is_create == True:
            self.contents[self.creating_index].create_branch(args)
        else:
            self.contents.append(Branch(self.level -1, self.coords, self.creating_index, self))
            self.is_create = True

    def fill_branch(self, data):
        if self.is_create == True:
            self.contents[self.creating_index].fill_branch(data)
        else:
            self.contents.append(Leaf(self.level -1, self.coords, self.creating_index, self, data))
            self.creating_index += 1

    def close_branch(self, args):
        if self.is_create == True:
            if self.contents[self.creating_index].close_branch(args) == True:
                self.creating_index += 1
                self.is_create = False
            return False
        else:
            return True

    def get(self, coords, *requests):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.pos) and Geometry.coord_compare_less(coords, 0):
            next_coords = Geometry.coord_mod(coords, 2**self.level)
            return self.contents[Geometry.index_from_coords(Geometry.coord_div(next_coords, 2**(self.level-1)))].get(next_coords, *requests)
        else:
            return self.master.get(coords, *requests)

class RegOct():
    def __init__(self, max_level, file_name, setup=None):
        if setup == None:
            self.setup = {"default":"0x0"}
        else:
            self.setup = setup
        self.coords = None
        self.default = None
        self.level = max_level
        self.octree = Branch(max_level, [0, 0, 0], 0, self)
        self.file_name = file_name

    @classmethod
    def direct(cls, max_level, file_name, setup=None):
        out = cls(max_level, file_name, setup)
        builder = Builder(out)
        builder.load()
        return out

    def get(self, coords, *requests):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.octree.pos) and Geometry.coord_compare_less(coords, 0):
            return self.octree.get(coords, *requests)
        else:
            try:
                output = {}
                for request in requests:
                    output[request] = vars(self)[request]
                return output
            except KeyError:
                raise InvalidRequestCallError(self.__class__.__name__, request)

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
                        op_fl.write(f'{str(self.octree.get(coords, "default",)["default"])} ')
                    op_fl.write("\n")
                op_fl.write("\n")

    def check_validity(self, args):
        if args[root_key["level"]] != self.level:
            return False
        return True

class Builder(Branch):
    def __init__(self, master):
        self.master = master
        master.octree = self
        self.setup = master.setup
        self.file_name = master.file_name

    def load(self):
        Reader(self, self.file_name).run()

    def root(self, args):
        if self.master.check_validity(args):
            print(args[root_key["level"]], [0, 0, 0], args[root_key["pos"]], self.master)
            super().__init__(args[root_key["level"]], [0, 0, 0], args[root_key["pos"]], self.master)
        else:
            raise AttributeDesynchronisationError()

def correlate(setup, data):
    for attr in setup.items():
        try:
            print(f'{attr[0]} = {data[attr[1]]}')
        except KeyError:
            raise UnboundVartagError(attr[1], data)

