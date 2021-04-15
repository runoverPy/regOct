from ..Structures import Octree
from queue import LifoQueue
from struct import pack

# here octree instances and orc files will be compiled to onc files

def save(octree, file_name):
    comp = Compiler()
    with open(file_name, "wb") as io:
        for command in scanner(octree):
            io.write(comp.translate(command))

def scanner(octree):
    def process(data):
        nonlocal lastlevel
        for i in range(lastlevel - data["level"]):
            counter.put(0)
            lastlevel -= 1
            yield Command.create_node()
        
        yield Command.fill_node(data["data"])

        for i in range(increment_counter()):
            lastlevel += 1
            yield Command.close_node() 

    def increment_counter():
        if counter.empty():
            return 0 
        lastcount = counter.get()
        lastcount += 1
        if lastcount == 8:
            counter.task_done()
            return 1 + increment_counter()
        else:
            counter.put(lastcount)
            return 0

    lastlevel = octree.level
    counter = LifoQueue()
    yield Command.header()
    yield Command.seed(octree.level)
    for data in iter(octree):
        yield from process(data)

class Command:
    singletons = {
        None:"nlnd",
        Ellipsis:"vdnd",
        False:"fsnd",
        True:"trnd"
    }

    def __init__(self, cmd, value=None):
        self.cmd = cmd
        self.count = 1
        self.value = value

    def __str__(self):
        out = self.cmd
        if self.value is not None:
            out += " " + str(self.value)
        return out

    def __eq__(self, other):
        if type(other) == type(self):
            if other.cmd == self.cmd:
                if other.value == self.value:
                    return True
        return False

    @classmethod
    def header(cls, version="0.0.1"):
        return cls("header", version)

    @classmethod
    def seed(cls, level):
        return cls("seed", level)

    @classmethod
    def fill_node(cls, value):
        if value in cls.singletons:
            return cls(cls.singletons[value])
        else:
            return cls("flnd", value)

    @classmethod
    def create_node(cls):
        return cls("crnd")

    @classmethod
    def close_node(cls):
        return cls("clnd")
    
class Compiler:
    conversion = {
        'header':b'\x00', 'seed':b'\x01', 

        'crnd':b'\x04', 'nxnd':b'\x05', 'clnd':b'\x06', 'flnd':b'\x07', 
        'nlnd':b'\x08', 'vdnd':b'\x09', 'fsnd':b'\x0a', 'trnd':b'\x0b', 

          'i8':b'\x20',  'i16':b'\x21',  'i32':b'\x22',  'i64':b'\x23', 
         'ui8':b'\x24', 'ui16':b'\x25', 'ui32':b'\x26', 'ui64':b"\x27", 
         'f32':b'\x28',  'f64':b'\x29',  'c64':b'\x2a', 'c128':b'\x2b', 
         'Str':b'\x40', 'List':b'\x41', 'Dict':b'\x42',  'Set':b'\x43'
    }
    pystandard = {
        int: "i16", 
        float: "f64",
        complex: "c64",
        str: "Str",
        list: "List",
        dict: "Dict",
        set: "Set"
    }

    def translate(self, command:Command):
        return getattr(self, command.cmd)(command)

    def convert(self, value):
        return self.conversion[self.pystandard[type(value)]] + getattr(self, self.pystandard[type(value)])(value)

    def header(self, command:Command):
        return b"".join([self.conversion[command.cmd], self.convert(command.value)])
    def seed(self, command:Command):
        return b"".join([self.conversion[command.cmd], self.convert(command.value)])
    
    def crnd(self, command:Command):
        return b"".join([self.conversion[command.cmd], self.i8(command.count)])
    def nxnd(self, command:Command):
        return b"".join([self.conversion[command.cmd], self.i8(command.count)])
    def clnd(self, command:Command):
        return b"".join([self.conversion[command.cmd], self.i8(command.count)])
    def flnd(self, command:Command):
        return b"".join([self.conversion[command.cmd], self.i8(command.count), command.value])

    def nlnd(self, command:Command):
        return b"".join([self.conversion[command.cmd], self.i8(command.count)])
    def vdnd(self, command:Command):
        return b"".join([self.conversion[command.cmd], self.i8(command.count)])
    def fsnd(self, command:Command):
        return b"".join([self.conversion[command.cmd], self.i8(command.count)])
    def trnd(self, command:Command):
        return b"".join([self.conversion[command.cmd], self.i8(command.count)])
    
    # data types: return a value
    # basic data types
    
    def i8(self, value):
        return value.to_bytes(1, byteorder="big", signed=True)
    def i16(self, value):
        return value.to_bytes(2, byteorder="big", signed=True)
    def i32(self, value):
        return value.to_bytes(4, byteorder="big", signed=True)
    def i64(self, value):
        return value.to_bytes(8, byteorder="big", signed=True)

    def ui8(self, value):
        return value.to_bytes(1, byteorder="big", signed=False)
    def ui16(self, value):
        return value.to_bytes(2, byteorder="big", signed=False)
    def ui32(self, value):
        return value.to_bytes(4, byteorder="big", signed=False)
    def ui64(self, value):
        return value.to_bytes(8, byteorder="big", signed=False)

    def f32(self, value):
        return pack("f", value)
    def f64(self, value):
        return pack("d", value)
    def k64(self, value):
        return pack("ff", value.real, value.imag)
    def k128(self, value):
        return pack("dd", value.real, value.imag)

    # complex data types: iterated types
    def Str(self, value:str):
        return self.i8(len(value)) + value.encode()
    def List(self, value:list):
        return self.i8(len(value)) + b"".join(self.convert(item) for item in value)
    def Dict(self, value:dict):
        return self.i8(len(value)) + b"".join(self.convert(key) + self.convert(value) for key, value in value.items())
    def Set(self, value:set):
        return self.i8(len(value)) + b"".join(self.convert(item) for item in value)
