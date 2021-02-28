import math, sys, time
from enum import Enum, auto
from .Util import Geometry, SubdivisionIndexError, InvalidRequestCallError, UnboundVartagError, AttributeDesynchronisationError, ToasterBathError, root_key, header_key
from .Reader import Reader
from abc import ABC, abstractmethod
import warnings
from typing import final

class _OctreeInternal(ABC):
    def __init__(self, level, pos, master):
        self.level = level
        self.pos = pos
        self.master = master
        if self.level < 0:
            raise SubdivisionIndexError(self.level)

    def return_attrs(self, key, *requests):
        try:
            output = {}
            for request in requests:
                output[request] = vars(self)[request]
            return output
        except KeyError:
            pass
            raise InvalidRequestCallError(self.__class__.__name__, request)

class Leaf(_OctreeInternal):
    def __init__(self, level, pos, master, data):
        super().__init__(level, pos, master)
        # self.load_attrs(None, data)

    def load_attrs(self, setup, data):
        for attr in setup.items():
            try:
                setattr(self, attr[0], data[attr[1]])
            except KeyError:
                raise UnboundVartagError(attr[1], data)    

    def get(self, coords, minlevel=0, bounded=False):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.pos) and Geometry.coord_compare_less(coords, 0):
            return self
        else:
            if bounded:
                raise Exception
            else:
                return self.master.get(coords, minlevel)

class Void(_OctreeInternal):
    """WIP\nplaceholder class"""
    def __init__(self, level, pos, master):
        super().__init__(level, pos, master)

    @classmethod
    def null(cls):
        return cls(None, None, None)

    def to_leaf(self, data):
        self = Leaf(self.level, self.pos, self.master, data)

    def to_branch(self):
        self = Branch.void(self.level, self.pos, self.master)

    def get(self, coords, minlevel=0, bounded=False):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.pos) and Geometry.coord_compare_less(coords, 0):
            return self
        else:
            return self.master.get(coords, minlevel)

    def build_to(self, coords):...

class Branch(_OctreeInternal):
    def __init__(self, level, pos, master):
        super().__init__(level, pos, master)
        self.creating_index = 0
        self.end_of_line = True
        self.contents = []

    @classmethod
    def void(cls, level, pos, master):
        obj = cls(level, pos, master)
        obj.contents = list(Void(level -1, i, obj) for i in range(8))

    def get(self, coords, minlevel=0, bounded=False):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.pos) and Geometry.coord_compare_less(coords, 0):
            if self.level > minlevel:
                next_coords = Geometry.coord_mod(coords, 2**self.level)
                return self.contents[Geometry.index_from_coords(Geometry.coord_div(next_coords, 2**(self.level-1)))].get(next_coords, minlevel)
            else:
                raise Exception
        else:
            if bounded:
                raise Exception 
            else:
                return self.master.get(coords, minlevel)

    def __getitem__(self, pos_coord):
        return self.contents[Geometry.index_from_coords(pos_coord)]

    def __setitem__(self, pos_coord, data:_OctreeInternal):
        self.contents[Geometry.index_from_coords(pos_coord)] = data

class Builder(Branch):
    def __init__(self, master):
        self.master = master
        self.creating_index = 0
        self.end_of_line = True

    @classmethod
    def branch(cls, level, pos, master):
        obj = cls(master)
        obj.artefact = Branch(level, pos, master.artefact)
        obj.pos = pos
        return obj

    def push(self):
        self.master.octree = self.artefact

    def load(self, file_name):
        Reader.entangle(self, file_name).run()
    
    def header(self, data):
        if data["0x0"] != "0.0.2":
            warnings.warn("The ONC version of the file has been outdated.")
            if (output := input("UPDATE FILE: (y/n)\n"))[0] == "y":
                print("its definitely updating rn")
            elif output[0] == "n":
                print("your loss")
                time.sleep(1)
                raise ToasterBathError()

    def root(self, args):
        if self.master.check_validity(args):
            self.artefact = Branch(args[root_key["level"]], args[root_key["pos"]], self.master)
        else:
            raise AttributeDesynchronisationError()

    def create_branch(self, args):
        if self.end_of_line == False:
            self.artefact.contents[self.creating_index].create_branch(args)
        else:
            self.artefact.contents.append(Builder.branch(self.artefact.level -1, self.creating_index, self))
            self.end_of_line = False

    def fill_branch(self, data):
        if self.end_of_line == False:
            self.artefact.contents[self.creating_index].fill_branch(data)
        else:
            self.artefact.contents.append(Leaf(self.artefact.level -1, self.creating_index, self, data))
            self.creating_index += 1

    def close_branch(self, args):
        if self.end_of_line == False:
            if (branch := self.artefact.contents[self.creating_index].close_branch(args)) != None:
                self.artefact.contents[self.creating_index] = branch
                self.end_of_line = True
                self.creating_index += 1
            return None
        else:
            return self

class Octree:
    """The Class with which octrees will be created."""
    def __init__(self, max_level):
        self.level = max_level

    def get(self, coords):
        self.octree.get(coords, bounded=True)

    @classmethod
    def direct(cls, max_level, file_name):
        out = cls(max_level)
        Builder(out).load(file_name)
        return out

    def set_setup(self, setup):
        self.setup = setup

    def check_validity(self, args):
        if args[root_key["level"]] != self.level:
            return False
        return True

    @classmethod
    def subbranch(cls, coords, octree):
        """Clone a seperate subbranch to a new object"""
        branch = octree.get(coords)
        obj = cls(branch.level)
        obj.octree = branch
        return obj

    # Bottom-Up construction methods
    @classmethod
    def blank(cls, level):
        """Create a blank octree"""
        obj = cls(level)
        obj.octree = Void(obj.level, 0, obj)
        return obj

    def pullup(self, value=1):... # raise level of all below by value
    def newleaf(self, coords, data):...
    def setbranch(self, coords, data, subbranch_pos=None):... # set a branch to the contents of another octree, or its defined subbranch

class Addon(ABC):
    def __init__(self):
        self.card = "addon_base"

    @final
    @classmethod
    def bind(cls, bind_to):
        """The method called to bind a Addon to an octree"""
        obj = cls()
        setattr(bind_to, obj.card, obj)
        obj.branch = bind_to

    @final
    def get(self, coords4):
        return self.branch.get(coords4).__dict__[self.card]

def correlate(setup, data):
    for attr in setup.items():
        try:
            print(f'{attr[0]} = {data[attr[1]]}')
        except KeyError:
            raise UnboundVartagError(attr[1], data)
