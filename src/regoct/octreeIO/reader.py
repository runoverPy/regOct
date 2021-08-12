from io import BufferedReader
from queue import Queue
from struct import unpack
from typing import ContextManager
from contextlib import contextmanager

from ..Structures import Octree, Node, Leaf


def load(file_name):
    """
    The essential octree loading method.\n
    Use when the octree contains only contains built-in types, such as int, str, list and set.     
    """
    with open(file_name, "rb") as io:
        build_help = BuilderHelper()
        with build_help.build():
            for command in  Loader(io):
                build_help.route(command)
        return build_help.octree        


class Command:
    def __init__(self, name, count=1, value=None):
        self.command = name
        self.count = count
        self.value = value

    def __str__(self):
        out = self.command
        if self.value is not None:
            out += " " + str(self.value)
        return out


class Builder:
    def __init__(self, level, pos, master):
        self.level = level
        self.pos = pos
        self.master = master
        self.creating_index = 0
        self.end_of_line = True
        self.artefact:"list[Builder]" = []

    def crnd(self, *args):
        if self.end_of_line == False:
            self.artefact[self.creating_index].crnd()
        else:
            self.artefact.append(Builder(self.level -1, self.creating_index, self))
            self.end_of_line = False

    def flnd(self, data):
        if self.end_of_line == False:
            if self.artefact[self.creating_index].flnd(data):
                self.creating_index += 1
                self.end_of_line = True
        else:
            self.artefact.append(Leaf(self.level -1, self.creating_index, self, data))
            self.creating_index += 1
        
        if self.creating_index == 8:
            self.contents = self.artefact
            self.__class__ = Node
            del self.artefact
            del self.end_of_line
            del self.creating_index
            return True


class BuilderHelper(Builder):
    class VersionError(Exception):
        def __init__(self, given, required):
            self.message = f"Version {required} was required, but {given} was given"
            super().__init__(self.message)
    
    
    def __init__(self):
        pass


    def header(self, value):
        if value != "0.0.2":
            raise self.VersionError(value, "0.0.2")


    def seed(self, value):
        self.octree = Octree(value)
        super().__init__(self.octree.level+1, 0, None)


    def route(self, command:Command):
        for _ in range(command.count):
            getattr(self, command.command)(command.value)


    @contextmanager
    def build(self):
        try:
            yield self
        finally:
            self.octree.octree = self.artefact[0]


    def unfold(self):
        for _ in range(self.count):
            yield Command(name=self.command, value=self.value)


class Loader:
    commands = {
        b"\x00":"header", b"\x01":"seed",
        
        b"\x04":"crnd", b"\x07":"flnd", 
        b"\x08":"nlnd", b"\x09":"vdnd", b"\x0a":"fsnd", b"\x0b":"trnd",
        
        b"\x20":  "i8", b"\x21": "i16", b"\x22": "i32", b"\x23": "i64",
        b"\x24":  "u8", b"\x25": "u16", b"\x26": "u32", b"\x27": "u64",
        b"\x28": "f32", b"\x29": "f64", b"\x2a": "c64", b"\x2b":"c128",
        b"\x40": "Str", b"\x41":"List", b"\x42":"Dict", b"\x43":"Set"
    }


    def __init__(self, io:BufferedReader) -> None:
        self.io = io


    def __iter__(self):
        return self


    def __next__(self):
        if (next_byte := self.io.read(1)):
            return getattr(self, self.commands[next_byte])()
        else:
            raise StopIteration


    def get_next(self):
        if (next_byte := self.io.read(1)):
            return getattr(self, self.commands[next_byte])()
        else:
            raise StopIteration


    def header(self):
        return Command("header", value=self.get_next())
    
    def seed(self):
        return Command("seed", value=self.get_next())
    
    def crnd(self):
        return Command("crnd", self.u8())

    def flnd(self):
        return Command("flnd", self.u8(), self.get_next()) # here custom from_file method should be inserted

        
    def nlnd(self):
        return Command("flnd", self.u8())

    def vdnd(self):
        return Command("flnd", self.u8(), value=Ellipsis)

    def fsnd(self):
        return Command("flnd", self.u8(), value=False)

    def trnd(self):
        return Command("flnd", self.u8(), value=True)
        

    def i8(self):
        return int.from_bytes(self.io.read(1), byteorder="big", signed=True)

    def i16(self):
        return int.from_bytes(self.io.read(2), byteorder="big", signed=True)

    def i32(self):
        return int.from_bytes(self.io.read(4), byteorder="big", signed=True)

    def i64(self):
        return int.from_bytes(self.io.read(8), byteorder="big", signed=True)

    def u8(self):
        return int.from_bytes(self.io.read(1), byteorder="big", signed=False)

    def u16(self):
        return int.from_bytes(self.io.read(2), byteorder="big", signed=False)

    def u32(self):
        return int.from_bytes(self.io.read(4), byteorder="big", signed=False)

    def u64(self):
        return int.from_bytes(self.io.read(8), byteorder="big", signed=False)

    def f32(self):
        return unpack("f", self.io.read(4))

    def f64(self):
        return unpack("d", self.io.read(8))

    def c64(self):
        return complex(*unpack("ff", self.io.read(8)))

    def c128(self):
        return complex(*unpack("dd", self.io.read(16)))

    def Str(self):
        return self.io.read(self.u16()).decode()

    def List(self):
        return list(self.get_next() for _ in range(self.u16()))

    def Dict(self):
        return dict((self.get_next(), self.get_next()) for _ in range(self.u16()))

    def Set(self):
        return set(self.get_next() for _ in range(self.u16()))