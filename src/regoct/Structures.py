from contextlib import contextmanager
from copy import deepcopy
from warnings import warn

import tqdm

from .Util import Geometry, SubdivisionIndexError

class _OctreeInternal:
    def __init__(self, level):
        self.level = level
        if self.level < 0:
            raise SubdivisionIndexError(self.level)

    def setsubtree(self, src:"Leaf | Node"):
        if src.__class__ == Leaf:
            self.__class__ = Leaf
            self.value = deepcopy(src.value)
        elif src.__class__ == Node:
            self.__class__ = Node
            self.contents = list(src.contents[i].clone(self.level-1, self) for i in range(8))


class Leaf(_OctreeInternal):
    def __init__(self, level, data):
        super().__init__(level)
        self.value = data


    def clone(self):
        return Leaf(self.level, deepcopy(self.value))


    # Navigation Methods
    def get(self, coords):
        return self.value


    def set(self, coords, level) -> "Leaf | Node":
        if self.level == level:
            return self
        else:
            self.subdivide()
            return self.set(coords, level)


    def map(self, coords=[0,0,0], pos=0):
        next_coords = Geometry.coord_addition(Geometry.coords_from_index(pos, self.level), coords)
        return [{"coords":next_coords, "level":self.level, "void":bool(self), "data":self.value}]


    def count(self):
        return 1


    # Construction Methods
    def subdivide(self):
        self.__class__ = Node
        self.contents = list(Leaf(self.level-1, deepcopy(self.value)) for i in range(8))
        del self.value


    def setleaf(self, data):
        """sets value for leaf"""
        self.value = data


    def setnode(self, node):
        if node.__class__ == Leaf:
            self.value = deepcopy(node.value)
        elif node.__class__ == Node:
            self.__class__ = Node
            self.contents = list(member.clone(self.level-1, self) for member in node.contents)
            del self.value


    def defragment(self, counter:tqdm.tqdm):
        counter.update()


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
            return {"level":self.level, "void":bool(self), "data":self.value}


    def __eq__(self, o: "Leaf") -> bool:
        return self.__class__ == o.__class__ and self.value == o.value


class Node(_OctreeInternal):
    def __init__(self, level):
        super().__init__(level)
        self.contents = list(Leaf(level-1, None) for i in range(8))


    def clone(self, level):
        obj = Node(level)
        obj.contents = list(member.clone(obj.level-1, obj) for member in self.contents)
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


    def map(self, coords=[0,0,0], pos=0):
        out = []
        next_coords = Geometry.coord_addition(Geometry.coords_from_index(pos, self.level), coords)
        for pos, item in enumerate(self.contents):
            out.extend(item.map(next_coords, pos))
        return out


    def count(self):
        return sum(child.count() for child in self.contents)


    def subdivide(self):
        self.contents = list(self.clone(self.level-1, self) for _ in range(8))


    def setleaf(self, data=None):
        self.__class__ = Leaf
        self.value = data
        del self.contents


    def setnode(self, node):
        if node.__class__ == Leaf:
            self.__class__ = Leaf
            self.value = deepcopy(node.value)
        elif node.__class__ == Node:
            self.__class__ = Node
            self.contents = list(member.clone(self.level-1, self) for member in node.contents)


    def defragment(self, counter):
        for node in self.contents:
            node.defragment(counter)
        if all(self.contents[i] == self.contents[(i+1)%8] for i in range(8)):
            self.setleaf(self.contents[0].value)


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


    def __getitem__(self, key):
        return self.contents[key] 


    def __eq__(self, o: "Node"):
        return self.__class__ == o.__class__ and all(a == b for a, b in zip(self.contents, o.contents))


class Octree:
    def __init__(self, level, data=None):
        self.level = level
        self.octree:"Leaf | Node" = Leaf(self.level, data)


    # Navigation Methods
    def get(self, coords):
        if any((0 > value or value >= 2**self.level) for value in coords):
            return None
        else:
            return self.octree.get(coords)


    def set(self, coords, level):
        while self.level > level:
            self.superset()
        return self.octree.set(coords, level)


    def map(self):
        return self.octree.map()


    def get_octree(self):
        return self.octree


    def count(self):
        return self.octree.count()


    @contextmanager
    def edit(self):
        try:
            yield self
        finally:
            self.defragment()


    # Construction methods
    @classmethod
    def blank(cls, level, data=None):
        """Create a blank octree.\n
        Is functionally equal to simply calling the constructor and will be depricated in the near future."""
        obj = cls(level, data)
        return obj


    def subtree(self, coords, level):
        """Clone a seperate subtree to a new object"""
        node = self.get(coords, level)
        obj = Octree(node.level)
        obj.octree = node.clone(obj.level, obj)
        return obj


    def superset(self):
        obj = Node(self.level, 0, self)
        obj.contents = list(Leaf(obj.level-1, None) for _ in range(8))
        obj.contents[self.octree.pos] = self.octree
        self.octree = obj
        self.level += 1


    def set(self, coords, level, data):
        self.octree.set(coords, level).setleaf(data)


    def setsubtree(self, coords, level, src):
        """Insert a seperate Octree to the designated location"""
        self.octree.set(coords, level).setsubtree(src.octree)


    def defragment(self):
        counter = tqdm.tqdm(desc = "defragmentation in progress", total = self.octree.count())
        self.octree.defragment(counter)


    def __str__(self):
        return str(self.octree)


    def __iter__(self):
        self.iter = iter(self.octree)
        return self


    def __next__(self):
        return next(self.iter)

    
    def __eq__(self, o: "Octree") -> bool:
        return self.__class__ == o.__class__ and self.octree == o.octree