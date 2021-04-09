from queue import Queue
from struct import unpack, calcsize
from ..Structures import Octree, Node, Leaf

def load(file_name):
    cmdstream = Parser.read(file_name)
    cmd, lvl = next(cmdstream)
    if cmd != "seed":
        raise ValueError
    out = Octree(lvl)
    with BuilderHelper(out) as bh:
        for cmd, value in cmdstream:
            getattr(bh, cmd)(value)
    return out        

class Builder:
    def __init__(self, level, pos, master):
        self.level = level
        self.pos = pos
        self.master = master
        self.creating_index = 0
        self.end_of_line = True
        self.artefact = []

    def create_node(self, args):
        if self.end_of_line == False:
            self.artefact[self.creating_index].create_node(args)
        else:
            self.artefact.append(Builder(self.level -1, self.creating_index, self))
            self.end_of_line = False

    def close_node(self, args):
        if self.end_of_line == False:
            if self.artefact[self.creating_index].close_node(args):
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

    def fill_node(self, data):
        if self.end_of_line == False:
            self.artefact[self.creating_index].fill_node(data)
        else:
            self.artefact.append(Leaf(self.level -1, self.creating_index, self, data))
            self.creating_index += 1

class BuilderHelper(Builder):
    def __init__(self, octree):
        self.octree = octree
        super().__init__(octree.level+1, 0, None)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.octree.octree = self.artefact[0]

class VersionError(Exception):
    def __init__(self, given, required):
        self.message = f"Version {required} was required, but {given} was given"
        super().__init__(self.message)

class Command:
    commands = {
        "seed":["seed"],
        "crnd":["create_node"],
        "nxnd":["close_node", "create_node"],
        "clnd":["close_node"],
        "flnd":["fill_node"]
    }
    
    def __init__(self, name, count=1, value=None):
        self.command = name
        self.count = count
        self.value = value

    def process(self):
        out = []
        for item in zip(*list(self.commands[self.command] for i in range(self.count))):
            out += item
        for command in out:
            yield [command, self.value]

class Parser:
    commands = {
        b"\x00":"header", b"\x01":"seed",
        
        b"\x04":"crnd", b"\x05":"nxnd", b"\x06":"clnd", b"\x07":"flnd", 
        b"\x08":"nlnd", b"\x09":"vdnd", b"\x0a":"fsnd", b"\x0b":"trnd",
        
        b"\x20":  "i8", b"\x21": "i16", b"\x22": "i32", b"\x23": "i64",
        b"\x24": "ui8", b"\x25":"ui16", b"\x26":"ui32", b"\x27":"ui64",
        
        b"\x28": "f32", b"\x29": "f64", b"\x2a": "c64", b"\x2b":"c128",
        
        b"\x40": "Str", b"\x41":"List", b"\x42":"Dict", b"\x43":"Set"
    }
    
    def __init__(self, io):
        self.io = io

    @classmethod
    def read(cls, file_name):
        with open(file_name, "rb") as io:
            obj = cls(io)
            obj.run_next()
            while (next_byte := obj.io.read(1)):
                for command in getattr(obj, obj.commands[next_byte])().process():
                    yield command

    def run_next(self):
        if (next_byte := self.io.read(1)):
            return getattr(self, self.commands[next_byte])()
        else:
            raise EOFError

    # command structs: return a command object

    def header(self):
        if (fileversion := self.run_next()) != "0.0.1":
            raise VersionError(fileversion, "0.0.1")
        return Command("header", 1, fileversion)
    
    def seed(self):
        return Command("seed", value=self.run_next())
    
    def crnd(self):
        return Command("crnd", self.i8())
    def nxnd(self):
        return Command("nxnd", self.i8())
    def clnd(self):
        return Command("clnd", self.i8())
    def flnd(self):
        return Command("flnd", self.i8(), self.run_next())

    def nlnd(self):
        return Command("flnd", self.i8(), None)
    def vdnd(self):
        return Command("flnd", self.i8(), Ellipsis)
    def fsnd(self):
        return Command("flnd", self.i8(), False)
    def trnd(self):
        return Command("flnd", self.i8(), True)
    
    # data types: return a value
    # basic data types
    
    def i8(self):
        return int.from_bytes(self.io.read(1), byteorder="big", signed=True)
    def i16(self):
        return int.from_bytes(self.io.read(2), byteorder="big", signed=True)
    def i32(self):
        return int.from_bytes(self.io.read(4), byteorder="big", signed=True)
    def i64(self):
        return int.from_bytes(self.io.read(8), byteorder="big", signed=True)

    def ui8(self):
        return int.from_bytes(self.io.read(1), byteorder="big", signed=False)
    def ui16(self):
        return int.from_bytes(self.io.read(2), byteorder="big", signed=False)
    def ui32(self):
        return int.from_bytes(self.io.read(4), byteorder="big", signed=False)
    def ui64(self):
        return int.from_bytes(self.io.read(8), byteorder="big", signed=False)

    def f32(self):
        return unpack("f", self.io.read(4))
    def f64(self):
        return unpack("d", self.io.read(8))
    def k64(self):
        return complex(unpack("ff", self.io.read(8)))
    def k128(self):
        return complex(unpack("dd", self.io.read(16)))

    # complex data types: iterated types

    def Str(self):
        return self.io.read(self.i8()).decode()
    def List(self):
        return list(self.run_next() for i in range(self.i8()))
    def Dict(self):
        return dict((self.run_next(), self.run_next()) for i in range(self.i8()))
    def Set(self):
        return set(self.run_next() for i in range(self.i8()))

    def Srct(self):
        form = self.Str()
        return unpack(form, self.io.read(calcsize(form)))
