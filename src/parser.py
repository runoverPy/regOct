
from queue import Queue, LifoQueue
from abc import ABC, ABCMeta, abstractmethod


bytedelimiters = [b";", b","]
bytecommands = {b"\x00":"header", 
                b"\x04":"crnd", b"\x05":"nxnd", b"\x06":"clnd", b"\x07":"fllf", 
                b"\x08":"nllf", b"\x09":"vdlf", b"\x0a":"fslf", b"\x0b":"trlf",
                b"\x20":  "i8", b"\x21": "i16", b"\x22": "i32", b"\x23": "i64",
                b"\x24": "ui8", b"\x25":"ui16", b"\x26":"ui32", b"\x27":"ui64",
                b"\x28": "f32", b"\x29": "f64", b"\x2a": "c64", b"\x2b":"c128"}

bytetypes = {b"\x20":"i8", b"\x21":"i16", b"\x22":"i32", b"\x23":"i64", b"\x24":"ui8", b"\x25":"ui16", b"\x26":"ui32", b"\x27":"ui64"}

commands = {"!":"header", "/":"crnd", "%":"clnd", "&":"fllf"}

translatecommands = dict((v, k) for k, v in bytecommands.items())
translatetypes = {"'":b"\x21", '"':b"\x32", "*":b"\x34"} 

exclude = {b" ", b"\x0d\x0a"}
delimiters = [";", ","]

def lexer(file_name):
    with open(file_name, "rb") as data_file:
        command = []
        mcommand = bytes()
        for char in data_file.read():
            byte = char.to_bytes(1, byteorder="big", signed=True)
            if byte not in exclude:
                if byte == delimiters[0]:
                    command.append(mcommand)
                    mcommand = bytes()
                    print(command)
                    yield command
                    command = []
                else:
                    if byte == delimiters[1]:
                        command.append(mcommand)
                        mcommand = bytes()

                    else:
                        mcommand += byte

def read(file_name):
    with open(file_name, "r") as data_file:
        command = []
        mcommand = ""
        for char in data_file.read():
            if char not in {" ", "\n"}:
                if char == delimiters[0]:
                    command.append(mcommand)
                    mcommand = ""
                    yield command
                    command = []
                else:
                    if char == delimiters[1]:
                        command.append(mcommand)
                        mcommand = ""
                    else:
                        mcommand += char

def readbinary(file_name):
    with open(file_name, "rb") as openfile:
        while True:
            byte = openfile.read(1)
            if not byte:
                break
            print(byte)

def translate(src, dest):
    data = read(src)
    with open(dest, "wb") as dest_file:
        for command in data:
            print(command)
            dest_file.write(translatecommands[commands[command[0]]])
            try:
                dest_file.write(translatetypes[command[1][0]])
                dest_file.write(int(command[1][1]).to_bytes(1, byteorder="big", signed=False))
                
                dest_file.write(translatetypes[command[2][0]])
                print(command[2][2:])
                dest_file.write(int(command[2][2:]).to_bytes(int(command[2][1]), byteorder="big", signed=True))
            except IndexError:
                pass

def parse(file_name):
    out = Packet()
    with open(file_name, "rb") as openfile:
        while True:
            byte = openfile.read(1)
            if not byte:
                break
            if out.write(byte):
                print(out.read())

class Instr:
    def __init__(self, count:int, name:str, cont_type:type = dict, raw:bool = False):
        self.name = name
        self.count = count
        self.out = cont_type()
        self.raw = raw

    def read(self):
        return (self.name, self.out)

class Predef(Instr):
    def __init__(self, name, value):
        self.name = name
        self.count = 0
        self.out = value
        self.raw = True

    def read(self):
        return (self.name, self.out)

class Int(Instr): # notice the capitalisation
    def __init__(self, bytescount:int, signed:bool = True):
        super().__init__(bytescount, "int", bytes, True)
        self.raw = True
        self.signed = signed

    def read(self):
        return (self.name, int.from_bytes(self.out, byteorder="big", signed=self.signed))

class Packet:
    commands = bytecommands

    def __init__(self, count=4):
        if count == 0:
            self.subpacket = None
        else:
            self.subpacket = Packet(count-1)
        self.reset()

    def reset(self):
        self.count = 0
        self.instruction = None
        
    def __bool__(self):
        return self.count == self.instruction.count

    def write(self, byte):
        if self.instruction == None: # if self complete:
            getattr(self, self.commands[byte])() # load new instructions
        elif self.instruction.raw:
            self.count += 1
            self.instruction.out += byte
        elif self.subpacket.write(byte): # write to component
            self.add(self.subpacket.read()) # if component complete: hand data up
        return bool(self) # return if self complete

    def read(self): 
        tmp = self.instruction.read()
        self.reset()
        return tmp 

    def add(self, data:list):
        key, value = data
        self.instruction.out[key] = value
        self.count += 1
        
    def header(self):...
    def seed(self):...
    
    def crnd(self):
        self.instruction = Instr(0, "crnd")
    def nxnd(self):...
    def clnd(self):
        self.instruction = Instr(0, "clnd")
    def fllf(self):
        self.instruction = Instr(1, "fllf")

    def nllf(self):
        self.instruction = Predef("fllf", None)
    def vdlf(self):
        self.instruction = Predef("fllf", Ellipsis)
    def fslf(self):
        self.instruction = Predef("fllf", False)
    def trlf(self):
        self.instruction = Predef("fllf", True)
    
    def i8(self):
        self.instruction = Int(1)
    def i16(self):
        self.instruction = Int(2)
    def i32(self):
        self.instruction = Int(4)
    def i64(self):
        self.instruction = Int(8)

    def ui8(self):
        self.instruction = Int(1, False)
    def ui16(self):
        self.instruction = Int(2, False)
    def ui32(self):
        self.instruction = Int(4, False)
    def ui64(self):
        self.instruction = Int(8, False)
