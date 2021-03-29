from queue import Queue, LifoQueue

delimiters = [";", ","]

def parse_head():...
def parse_crnd():...
def parse_fllf():...
def parse_clnd():...

exclude = {" ", "\n"}

def lexer(file_name):
    with open(file_name, "r") as data_file:
        command = []
        mcommand = ""
        for char in data_file.read():
            print(char)
            if char not in exclude:
                if char == delimiters[0]:
                    command.append(mcommand)
                    mcommand = ""
                    print("#", command)
                    yield command
                    command = []
                else:
                    if char == delimiters[1]:
                        command.append(mcommand)
                        mcommand = ""
                    else:
                        mcommand += char


class interpreter:
    commands = {"!":"header", "/":"create_branch", "%":"close_branch", "&":"fill_branch"}
    types = {"i":int, "s":str, "t":True, "f":False, "n":None, "y":Ellipsis, "*":"iterations"}
    


class command(interpreter):
    def __init__(self, operator):
        self.operation = operator
        self.iterations = 1
        self.parameters = None
        self.buffer = bytes()
    
    def __call__(self, target):
        getattr(target, self.operation)(self.parameters)
        
    def write(self, byte):
        self.buffer += byte
        
class attribute(interpreter):
    def __init__(self, operator):
        self.operation = operator