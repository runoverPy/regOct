import math, sys, time
from enum import Enum, auto
from .Util import Geometry, SubdivisionIndexError, InvalidRequestCallError, UnboundVartagError, AttributeDesynchronisationError, ToasterBathError, root_key, header_key
from .Reader import Reader
from abc import ABC, abstractmethod
import warnings
from typing import final

class _OctreeInternal:
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
        self.setleaf(data)

    def clone(self, level, pos, master):
        return Leaf(level, pos, master, self.value)

    def get(self, coords, minlevel=0, bounded=False):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.pos) and Geometry.coord_compare_less(coords, 0):
            return self
        else:
            if bounded:
                raise Exception
            else:
                return self.master.get(coords, minlevel)

    def construct(self, coords, level, truncate=False):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.pos) and Geometry.coord_compare_less(coords, 0):
            if self.level == level:
                return self
            else:
                self.subdivide(truncate)
                return self.construct(coords, level, truncate=truncate)
        else:
            return self.master.construct(coords, truncate=truncate)

    def map(self, coords=[0,0,0]):
        next_coords = Geometry.coord_addition(Geometry.coords_from_index(self.pos, self.level), coords)
        return [{"coords":next_coords, "level":self.level, "pos":self.pos, "type":self.__class__, "void":self.is_void, "data":self.value}]

    def subdivide(self, truncate=False):
        if truncate:
            template = None
        else:
            template = self.value
        self.to_branch()
        self.contents = list(Leaf(self.level-1, i, self, template) for i in range(8))

    def setleaf(self, data):
        """sets value for leaf"""
        if data is None:
            self.value = None
            self.is_void = True
        else:
            self.value = data
            self.is_void = False

    def to_branch(self):
        self.__class__ = Branch
        del self.value
        del self.is_void

    def setbranch(self, src):
        if src.__class__ == Branch:
            self.to_branch()
            print(id(self), id(src))
            self.setbranch(src)


class Branch(_OctreeInternal):
    def __init__(self, level, pos, master):
        super().__init__(level, pos, master)
        self.contents = []

    def clone(self, level, pos, master):
        obj = Branch(level, pos, master)
        print(self.contents)
        obj.contents = list(self.contents[i].clone(obj.level-1, i, obj) for i in range(8))
        return obj

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

    def construct(self, coords, level, truncate=False):
        if Geometry.coord_div(coords, 2**self.level) == Geometry.coords_from_index(self.pos) and Geometry.coord_compare_less(coords, 0):
            if self.level == level:
                return self
            else:
                next_coords = Geometry.coord_mod(coords, 2**self.level)
                return self.contents[Geometry.index_from_coords(Geometry.coord_div(next_coords, 2**(self.level-1)))].construct(next_coords, level, truncate=truncate)
        else:
            return self.master.construct(coords, truncate=truncate)

    def map(self, coords=[0,0,0]):
        out = []
        next_coords = Geometry.coord_addition(Geometry.coords_from_index(self.pos, self.level), coords)
        for i in self.contents:
            out.extend(i.map(next_coords))
        return out

    def to_leaf(self):
        self.__class__ = Leaf
        del self.contents

    def setbranch(self, src):
        print(self.level, src.contents)
        self.contents = list(src.contents[i].clone(self.level-1, i, self) for i in range(8))

    def __getitem__(self, pos_coord:list):
        return self.contents[Geometry.index_from_coords(pos_coord)]

    def __setitem__(self, pos_coord:list, src):
        if src.__class__ == Branch:
            self.contents = list(Branch.clone(self.level-1, i, self, src.contents[i]) for i in range(8))
        else:
            self.to_leaf()

class Builder:
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

    def load(self, file_name):
        Reader.entangle(self, file_name).run()
        self.master.octree = self.artefact

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
                print(branch)
                self.end_of_line = True
                self.creating_index += 1
            return None
        else:
            # the superiors octree attribute must be edited here
            print(self.artefact.__dict__)
            return self.artefact

class Octree:
    """The Class with which octrees will be created."""
    def __init__(self, max_level):
        self.level = max_level

    def get(self, coords):
        return self.octree.get(coords, bounded=True)

    @classmethod
    def direct(cls, max_level, file_name):
        out = cls(max_level)
        Builder(out).load(file_name)
        return out

    def check_validity(self, args):
        if args[root_key["level"]] != self.level:
            return False
        return True

    # Bottom-Up construction methods
    @classmethod
    def blank(cls, level):
        """Create a blank octree"""
        obj = cls(level)
        obj.octree = Leaf(obj.level, 0, obj, None)
        return obj

    def subbranch(self, coords):
        """Clone a seperate subbranch to a new object"""
        branch = self.get(coords)
        obj = Octree(branch.level)
        obj.octree = branch
        return obj

    def setleaf(self, coords, level, data):
        self.octree.construct(coords, level).setleaf(data)

    def setbranch(self, coords, level, src):
        """Insert a seperate Octree to the designated location"""
        self.octree.construct(coords, level).setbranch(src.octree)

    def map(self):
        return self.octree.map()


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