from ..Structures import Octree
from queue import LifoQueue

# here octree instances and orc files will be compiled to onc files

def save(file_name):...

def readout(octree):
    for dataset in iter(octree):
        print(dataset)
    
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



class Scanner:
    pystandard = {
        int: "i16", 
        float: "f64",
        complex: "c64",
        str: "Str",
        list: "List",
        dict: "Dict",
        set: "Set"
    }
    singletons = {
        None:"nlnd",
        Ellipsis:"vdnd",
        False:"fsnd",
        True:"trnd"
    }

    def __init__(self, octree):
        self.octree = octree
        self.lastlevel = octree.level
        self.counter = LifoQueue()
        # on each node wrapper call, add int 0

    def breakdown(self):
        yield self.header()
        yield self.seed()
        for data in iter(self.octree):
            yield from self.process(data)

    def header(self):
        return ["header", "0.0.1"]
    def seed(self):
        return ["seed", self.octree.level]

    def count(self):...

    def process(self, data):
        for i in range(self.lastlevel - data["level"]):
            self.counter.put(0)
            self.lastlevel -= 1
            yield ["crnd"]
        
        if data["data"] in self.singletons:
            yield [self.singletons[data["data"]]]
        else:
            yield ["flnd"]

        for i in range(self.increment_counter()):
            self.lastlevel += 1
            yield ["clnd"] 

    def increment_counter(self):
        if self.counter.empty():
            return 0 
        lastcount = self.counter.get()
        lastcount += 1
        if lastcount == 8:
            self.counter.task_done()
            return 1 + self.increment_counter()
        else:
            self.counter.put(lastcount)
            return 0

