from io import BufferedReader
from struct import unpack
from copy import deepcopy
from contextlib import contextmanager

from .structures import Octree, Node, Leaf


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
    def __init__(self, level):
        self.level = level
        self.creating_index = 0
        self.end_of_line = True
        self.artefact:"list[Builder]" = []

    def crnd(self, *args):
        if self.end_of_line == False:
            self.artefact[self.creating_index].crnd()
        else:
            self.artefact.append(Builder(self.level-1))
            self.end_of_line = False

    def flnd(self, data):
        if self.end_of_line == False:
            if self.artefact[self.creating_index].flnd(data):
                self.creating_index += 1
                self.end_of_line = True
        else:
            self.artefact.append(Leaf(self.level -1, data))
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
        super().__init__(value + 1)


    def route(self, command:Command):
        for _ in range(command.count):
            getattr(self, command.command)(deepcopy(command.value))


    @contextmanager
    def build(self):
        try:
            yield self
        finally:
            self.octree.octree = self.artefact[0]


class LoadingStream:
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


    def convert(self):
        return getattr(self, self.commands[self.read()])()
        

    def read(self) -> bytes:
        if (next_byte := self.io.read(1)):
            return next_byte
        else:
            raise EOFError


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
        return list(self.convert() for _ in range(self.u16()))

    def Dict(self):
        return dict((self.convert(), self.convert()) for _ in range(self.u16()))

    def Set(self):
        return set(self.convert() for _ in range(self.u16()))


class Loader:
    commands = {
        b"\x00":"header", b"\x01":"seed",
        
        b"\x04":"crnd", b"\x07":"flnd", 
        b"\x08":"nlnd", b"\x09":"vdnd", b"\x0a":"fsnd", b"\x0b":"trnd",
    }


    def __init__(self, io:BufferedReader, factory) -> None:
        self.factory = factory
        self.converter = LoadingStream(io)


    def __iter__(self):
        return self


    def __next__(self):
        try:
            return getattr(self, self.commands[self.converter.read()])()
        except EOFError:
            raise StopIteration


    def header(self):
        return Command("header", value=self.converter.convert())
    
    def seed(self):
        return Command("seed", value=self.converter.convert())
    
    def crnd(self):
        return Command("crnd", self.converter.u8())

    def flnd(self):
        return Command("flnd", self.converter.u8(), self.factory.from_file(self.factory, self.converter)) # here custom from_file method should be inserted

        
    def nlnd(self):
        return Command("flnd", self.converter.u8())

    def vdnd(self):
        return Command("flnd", self.converter.u8(), value=Ellipsis)

    def fsnd(self):
        return Command("flnd", self.converter.u8(), value=False)

    def trnd(self):
        return Command("flnd", self.converter.u8(), value=True)
