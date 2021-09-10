from io import BufferedWriter
from queue import LifoQueue
from struct import pack
  


def scanner(octree):
    def process(data):
        nonlocal lastlevel
        for i in range(lastlevel - data["level"]):
            counter.put(0)
            lastlevel -= 1
            yield Command.create_node()
        
        yield Command.fill_node(data["data"])
        lastlevel += increment_counter()
        
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
    command:Command = None
    for data in iter(octree):
        for nxtcmd in process(data):
            if command is None:
                command = nxtcmd
            elif nxtcmd == command:
                command.count += 1
            else:
                yield command
                command = nxtcmd
    yield command


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
    def header(cls, version="0.0.2"):
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


class SavingStream:
    types = {
          'i8':b'\x20',  'i16':b'\x21',  'i32':b'\x22',  'i64':b'\x23', 
          'u8':b'\x24',  'u16':b'\x25',  'u32':b'\x26',  'u64':b"\x27", 
         'f32':b'\x28',  'f64':b'\x29',  'c64':b'\x2a', 'c128':b'\x2b', 
        "flse":b"\x2c", "true":b"\x2d", 
         'Str':b'\x40', 'List':b'\x41', 'Dict':b'\x42',  'Set':b'\x43'
    }
    py_standard = {
        int: "i32", 
        float: "f64",
        complex: "c64",
        str: "Str",
        list: "List",
        dict: "Dict",
        set: "Set"
    }

    
    def __init__(self, io:BufferedWriter) -> None:
        self.io = io


    def convert(self, value):
        type_byte = self.py_standard[type(value)]
        self.io.write(self.types[type_byte])
        getattr(self, type_byte)(value)


    def write(self, value:bytes):
        self.io.write(value)


    def i8(self, value:int):
        self.io.write(value.to_bytes(1, byteorder="big", signed=True))

    def i16(self, value:int):
        self.io.write(value.to_bytes(2, byteorder="big", signed=True))

    def i32(self, value:int):
        self.io.write(value.to_bytes(4, byteorder="big", signed=True))

    def i64(self, value:int):
        self.io.write(value.to_bytes(8, byteorder="big", signed=True))

    def u8(self, value:int):
        self.io.write(value.to_bytes(1, byteorder="big", signed=False))
    
    def u16(self, value:int):
        self.io.write(value.to_bytes(2, byteorder="big", signed=False))

    def u32(self, value:int):
        self.io.write(value.to_bytes(4, byteorder="big", signed=False))

    def u64(self, value:int):
        self.io.write(value.to_bytes(8, byteorder="big", signed=False))

    def f32(self, value:float):
        self.io.write(pack("f", value))

    def f64(self, value:float):
        self.io.write(pack("d", value))

    def c64(self, value:complex):
        self.io.write(pack("ff", value.real, value.imag))

    def c128(self, value:complex):
        self.io.write(pack("dd", value.real, value.imag))

    def Str(self, value:str):
        self.u16(len(value))
        self.io.write(value.encode())

    def List(self, value:list):
        self.u16(len(value))
        for item in value:
            self.convert(item) 

    def Dict(self, value:dict):
        self.u16(len(value))
        for key, value in value.items():
            self.convert(key); self.convert(value) 

    def Set(self, value:set):
        self.u16(len(value))
        for item in value:
            self.convert(item) 


class Saver:
    conversion = {
        'header':b'\x00', 'seed':b'\x01', 

        'crnd':b'\x04', 'flnd':b'\x07', 
        'nlnd':b'\x08', 'vdnd':b'\x09', 'fsnd':b'\x0a', 'trnd':b'\x0b', 
    }


    def __init__(self, io:BufferedWriter, factory) -> None:
        self.factory = factory
        self.converter = SavingStream(io)


    def translate(self, command:Command):
        """Routes the incoming commands that a octree decomposes into towards the individual transcription commands"""
        getattr(self, command.cmd)(command)
    

    def header(self, command:Command):
        self.converter.write(self.conversion[command.cmd])
        self.converter.convert(command.value)

    def seed(self, command:Command):
        self.converter.write(self.conversion[command.cmd])
        self.converter.convert(command.value)

    def crnd(self, command:Command):
        self.converter.write(self.conversion[command.cmd])
        self.converter.u8(command.count)

    def flnd(self, command:Command):
        self.converter.write(self.conversion[command.cmd])
        self.converter.u8(command.count)
        self.factory.to_file(command.value, self.converter)
    
    def nlnd(self, command:Command):
        self.converter.write(self.conversion[command.cmd])
        self.converter.u8(command.count)

    def vdnd(self, command:Command):
        self.converter.write(self.conversion[command.cmd])
        self.converter.u8(command.count)

    def fsnd(self, command:Command):
        self.converter.write(self.conversion[command.cmd])
        self.converter.u8(command.count)

    def trnd(self, command:Command):
        self.converter.write(self.conversion[command.cmd])
        self.converter.u8(command.count)


