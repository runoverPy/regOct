from .Structures import Octree, Leaf, Node
from .Reader import Reader

def load(file_name):
    datastream = Reader.run_as_generator(file_name)
    next(datastream)


def save(octree, file_name):...

class Builder:
    def __init__(self, level, pos, master):
        self.level = level
        self.pos = pos
        self.master = master
        self.creating_index = 0
        self.end_of_line = True
        self.artefact = []

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
