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

    def setsubtree(self, src):
        self.master.replaceslot(self.pos, src.clone(self.level, self.pos, self.master))
        self.destruct()

    def destruct(self):...

class Leaf(_OctreeInternal):
    def __init__(self, level, pos, master, data):
        super().__init__(level, pos, master)
        self.setleaf(data)

    def destruct(self):
        del self.master

    def clone(self, level, pos, master):
        return Leaf(level, pos, master, self.value)

    # Navigation Methods
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
        return [{"coords":next_coords, "level":self.level, "pos":self.pos, "type":self.__class__, "void":bool(self), "data":self.value}]

    # Construction Methods
    def subdivide(self, truncate=False):
        if truncate:
            template = None
        else:
            template = self.value
        del self.value
        self.__class__ = Node
        self.contents = list(Leaf(self.level-1, i, self, template) for i in range(8))

    def setleaf(self, data):
        """sets value for leaf"""
        self.value = data

    # Spec Methods
    def __str__(self):
        return str({"level":self.level, "pos":self.pos, "type":self.__class__, "void":bool(self), "data":self.value})

    def __bool__(self):
        return self.value is None or self.value == []

    def __iter__(self):
        self.has_returned = False
        return self

    def __next__(self):
        if self.has_returned:
            raise StopIteration
        else:
            self.has_returned = True
            return [{"level":self.level, "pos":self.pos, "type":self.__class__, "void":bool(self), "data":self.value}]

class Node(_OctreeInternal):
    def __init__(self, level, pos, master, template=None):
        super().__init__(level, pos, master)
        self.contents = list(Leaf(level-1, i, self, template) for i in range(8))

    def destruct(self):
        del self.master
        for i in self.contents:
            i.destruct()
        del self.contents

    def clone(self, level, pos, master):
        obj = Node(level, pos, master)
        obj.contents = list(self.contents[i].clone(obj.level-1, i, obj) for i in range(8))
        return obj

    # Navigation Methods
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

    # Construction Methods
    def replaceslot(self, pos, new):
        self.contents[pos] = new

    def subdivide(self):
        self.contents = list(self.clone(self.level-1, i, self) for i in range(8))

    def setleaf(self, data=None):
        self.master.replaceslot(self.pos, Leaf(self.level, self.pos, self.master, data))
        self.destruct()

    # Spec Methods
    def __str__(self):
        return "\n".join(str(i) for i in self.contents)

    def __iter__(self):
        self.n = 0
        self.reading = iter(self.contents[0])
        return self

    def __next__(self):
        try:
            out = next(self.reading)
        except StopIteration:
            self.n += 1
            if self.n == 8:
                raise StopIteration
            self.reading = iter(self.contents[self.n])
            out = next(self.reading)
        return out

class Builder(_OctreeInternal):
    def __init__(self, level, pos, master):
        super().__init__(level, pos, master)
        self.creating_index = 0
        self.end_of_line = True
        self.artefact = []


    @classmethod
    def load(cls, octree, file_name):
        obj = cls(0, 0, octree)        
        Reader.entangle(obj, file_name).run()
        return obj

    def header(self, data):
        if data[0] != "0.0.2":
            warnings.warn("The ONC version of the file has been outdated.")
            if (output := input("UPDATE FILE: (y/n)\n"))[0] == "y":
                print("its definitely updating rn")
            elif output[0] == "n":
                print("your loss")
                time.sleep(1)
                raise ToasterBathError()
    
    def root(self, data):
        self.master.level = data[0]
        self.level = data[0]

    def create_branch(self, args):
        if self.end_of_line == False:
            self.artefact[self.creating_index].create_branch(args)
        else:
            self.artefact.append(Builder(self.level -1, self.creating_index, self))
            self.end_of_line = False

    def fill_branch(self, data):
        if self.end_of_line == False:
            self.artefact[self.creating_index].fill_branch(data)
        else:
            self.artefact.append(Leaf(self.level -1, self.creating_index, self, data))
            self.creating_index += 1

    def close_branch(self, args):
        if self.end_of_line == False:
            if self.artefact[self.creating_index].close_branch(args):
                self.creating_index += 1
                self.end_of_line = True
            return False
        else:
            self.contents = self.artefact
            self.__class__ = Node
            del self.artefact
            del self.end_of_line
            del self.creating_index
            return True

class Octree:
    """The Class with which octrees will be created.
    It is the Root of the Octree.
    It acts as a quasi-node, with only one slot"""
    def __init__(self, max_level):
        self.level = max_level
        self.octree = None

    # Navigation Methods
    def get(self, coords, minlevel=0, bounded=False):
        if self.level > minlevel:
            return self.octree.get(coords, minlevel, bounded)
        else:
            raise Exception

    def construct(self, coords, level, truncate=False):
        while self.level >= level:
            self.superset()
        return self.octree.construct(coords, level, truncate=truncate)

    def map(self):
        return self.octree.map()

    # Load From File
    @classmethod
    def load(cls, file_name):
        out = cls(None)
        out.octree = Builder.load(out, file_name)
        return out

    # Construction methods
    @classmethod
    def blank(cls, level, data=None):
        """Create a blank octree"""
        obj = cls(level)
        obj.octree = Leaf(obj.level, 0, obj, data)
        return obj

    def subtree(self, coords, level):
        """Clone a seperate subtree to a new object"""
        node = self.get(coords, level)
        obj = Octree(node.level)
        obj.octree = node.clone(obj.level, 0, obj)
        return obj

    def superset(self):
        obj = Node(self.level, 0, self)
        obj.contents = list(Leaf(obj.level-1, i, obj, None) for i in range(8))
        obj.contents[self.octree.pos] = self.octree
        self.octree.master = obj
        self.octree = obj
        self.level += 1

    def replaceslot(self, pos, new):
        self.octree = new

    def setleaf(self, coords, level, data):
        self.octree.construct(coords, level).setleaf(data)

    def setsubtree(self, coords, level, src):
        """Insert a seperate Octree to the designated location"""
        self.octree.construct(coords, level).setsubtree(src.octree)

    def __str__(self):
        return str(self.octree)

    def __iter__(self):
        self.iter = iter(self.octree)
        return self

    def __next__(self):
        return next(self.iter)

class Addon(ABC):
    def __init__(self):
        self.card = "addon_base"

    @final
    @classmethod
    def bind(cls, bind_to):
        """The method called to bind a Addon to an octree"""
        obj = cls()
        setattr(bind_to, obj.card, obj)
        obj.node = bind_to

    @final
    def get(self, coords4):
        return self.node.get(coords4).__dict__[self.card]