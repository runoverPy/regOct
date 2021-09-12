from contextlib import contextmanager
from copy import deepcopy
import math

from .Util import Geometry


class Leaf:
    def __init__(self, level, data):
        self.value = data
        self.level = level
        if self.level < 0:
            raise ValueError(self.level)


    def clone(self, level):
        return Leaf(self.level, deepcopy(self.value))


    def get(self, coords):
        return self.value


    def set(self, coords, level) -> "Leaf | Node":
        if self.level == level:
            return self
        else:
            self.subdivide()
            return self.set(coords, level)


    def subdivide(self):
        self.__class__ = Node
        self.contents = list(Leaf(self.level-1, deepcopy(self.value)) for i in range(8))
        del self.value


    def make_leaf(self, data):
        """sets value for leaf"""
        self.value = data


    def make_node(self, node):
        if node.__class__ == Leaf:
            self.value = deepcopy(node.value)
        elif node.__class__ == Node:
            self.__class__ = Node
            self.contents = list(member.clone(self.level-1) for member in node.contents)
            del self.value


    def defragment(self):...


    def __str__(self):
        return str({"level":self.level, "data":str(self.value)})


    def __bool__(self):
        return bool(self.value) 


    def __iter__(self):
        self.has_returned = False
        return self


    def __next__(self):
        if self.has_returned:
            raise StopIteration
        else:
            self.has_returned = True
            return {"coords": (0, 0, 0), "level":self.level, "void":bool(self), "data":self.value}


    def __len__(self):
        return 1


    def __eq__(self, o: "Leaf") -> bool:
        return self.__class__ == o.__class__ and self.value == o.value


class Node:
    def __init__(self, level):
        self.contents = list(Leaf(level-1, None) for i in range(8))
        self.level = level
        if self.level < 0:
            raise ValueError(self.level)


    def clone(self, level):
        obj = Node(level)
        obj.contents = list(member.clone(obj.level-1) for member in self.contents)
        return obj


    # Navigation Methods
    def get(self, coords):
        next_coords = Geometry.coord_mod(coords, 2**self.level)
        next_index = Geometry.index_from_coords(Geometry.coord_div(next_coords, 2**(self.level-1)))
        return self.contents[next_index].get(next_coords)
        

    def set(self, coords, level) -> "Leaf | Node":
        if self.level == level:
            return self
        else:
            next_coords = Geometry.coord_mod(coords, 2**self.level)
            next_index = Geometry.index_from_coords(
                Geometry.coord_div(
                    next_coords,
                    2**(self.level-1)
                )
            )
            return self.contents[next_index].set(next_coords, level)


    def subdivide(self):
        self.contents = list(self.clone(self.level-1) for _ in range(8))


    def make_leaf(self, data=None):
        self.__class__ = Leaf
        self.value = data
        del self.contents


    def make_node(self, node):
        if node.__class__ == Leaf:
            self.__class__ = Leaf
            self.value = deepcopy(node.value)
        elif node.__class__ == Node:
            self.__class__ = Node
            self.contents = list(member.clone(self.level-1) for member in node.contents)


    def defragment(self):
        for node in self.contents:
            node.defragment()
        if all(self.contents[i] == self.contents[(i+1)%8] for i in range(8)):
            self.make_leaf(self.contents[0].value)


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
        out["coords"] = tuple(a + b for a, b in zip(Geometry.coords_from_index(self.n, self.level - 1), out["coords"]))
        return out


    def __len__(self):
        return sum(len(child) for child in self)


    def __eq__(self, o: "Leaf | Node"):
        return self.__class__ == o.__class__ and all(a == b for a, b in zip(self.contents, o.contents))


class Octree:
    def __init__(self, level, data=None):
        self.octree:"Leaf | Node" = Leaf(level, data)
        self.level = level


    def _get(self, coords):
        if any(0 > value >= 2**self.level for value in coords):
            raise IndexError()
        else:
            return self.octree.get(coords)


    def _set(self, coords, level) -> "Leaf | Node":
        if any(0 > value >= 2**self.level for value in coords):
            print("out of range")
            raise IndexError()
        return self.octree.set(coords, level)


    def _raise(self):
        print("raising")
        new_octree = Node(self.level + 1, 0, self)
        new_octree.contents = list(Leaf(self.level, None) for _ in range(8))
        new_octree.contents[0] = self.octree
        self.octree = new_octree


    @contextmanager
    def edit(self):
        try:
            yield self
        finally:
            self.octree.defragment()

    # WIP
    def get_sub_tree(self, coords: "tuple", level) -> "Octree":
        """-WIP- Clone a segment of the octree to a new object"""
        node = self._set(coords, level)
        obj = Octree(node.level)
        obj.octree = node.clone(obj.level)
        return obj


    def set_sub_tree(self, coords: "tuple", level, src: "Octree"):
        """-WIP- Insert a seperate Octree to the designated location"""
        self._set(coords, level).make_node(src.octree)


    # spec methods
    def __str__(self):
        return str(self.octree)


    def __iter__(self):
        return iter(self.octree)
    

    def __getitem__(self, index: "tuple"):
        if len(index) != 3:
            raise TypeError("octree key must be a 3-tuple (x, y, z)")
        return self._get(index) 


    def __setitem__(self, index: "tuple", data):
        if len(index) == 3:
            index = (*index, 0)
        if len(index) != 4:
            raise TypeError("octree key must be a 3- or 4-tuple (x, y, z[, level])")
        self._set(index[:3], index[3]).make_leaf(data)


    def __len__(self):
        return len(self.octree)


    def __eq__(self, o: "Octree") -> bool:
        return self.__class__ == o.__class__ and self.octree == o.octree

    
    def __ne__(self, o: "Octree") -> bool:
        return not self == o