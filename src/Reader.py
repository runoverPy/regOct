from queue import Queue

class Reader:
    def __init__(self, file_name):
        self.output = []
        self.direct_output = False
        self.file_name = file_name
        self.commands = [
            {"!":"header", "?":"root", "/":"create_branch", "&":"fill_branch", "#":"close_branch"},     # Commands
            {'"':"set_value", "'":"set_value", "*":"set_iterations", "@":"set_vartag", ";":"finish"},   # Modifiers
            {'"':"load_char", "'":"load_int"}]                                                          # Parameters

        self.processes = ["assign_command", "assign_modifier", "run_modifier"]
        self.state = [0, "", ""]        # Active Process | Active Modifier | Active Parameter
        self.data = ["", {}, 1]         # Command | Parameters | Iterations 
        self.buffer = ["", "", 0]       # VarTag | DataString | Chars Remaining

    @classmethod
    def entangle(cls, target, file_name):
        out = cls(file_name)
        out.target = target
        out.direct_output = True
        return out

    def run(self):
        with open(self.file_name, "r") as data_file:
                all_data = data_file.read()
                for b in all_data:
                    if b != " " and b != "\n":
                        getattr(self, self.processes[self.state[0]])(b)

    def run_as_generator(self):
        with open(self.file_name, "r") as data_file:
                while (char := data_file.read(1)) != "":
                    if char != " " and char != "\n":
                        if char == ";" and self.state[0] == 1:
                            yield self.data
                            self.state = [0, "", ""]
                            self.data = ["", {}, 1]
                        else:
                            getattr(self, self.processes[self.state[0]])(char)

    def read_bits(self):
        with open(self.file_name, "rb") as data_file:
                all_data = data_file.read()
                for b in all_data:
                    b = hex(int(b)) 
                    if b != " " and b != "\n":
                        print(b)

    def update_machine(self, char):
        if char != " " and char != "\n":
            getattr(self, self.processes[self.state[0]])(char)

    # Assigning Methods
    def assign_command(self, cmd):
        self.data[0] = self.commands[0][cmd]
        self.state[0] = 1

    def assign_modifier(self, mod):
        if mod == ";":
            self.finish()
        else:
            self.state[1] = self.commands[1][mod]
            if mod in self.commands[2]:
                self.state[2] = self.commands[2][mod]
            self.state[0] = 2

    def run_modifier(self, args):
        getattr(self, self.state[1])(args)

    # Modifiying Methods
    def set_value(self, val):
        if self.buffer[2] == 0:
            self.buffer[2] = int(val)
        else:
            self.buffer[1] += val
            self.buffer[2] -= 1
        if self.buffer[2] == 0:
            self.data[1][self.buffer[0]] = getattr(self, self.state[2])(self.buffer[1])
            self.buffer = ["", "", 0]
            self.state[0] = 1

    def set_vartag(self, vartag):
        self.state[0] = 1
        self.buffer[0] = str(hex(int(vartag)))

    def set_iterations(self, iters):
        self.state[0] = 1
        self.data[2] = int(iters)

    # State Methods
    def load_char(self, chars):
        return str(chars)

    def load_int(self, ints):
        return int(ints)

    # Push Methods
    def finish(self):
        if not self.direct_output:
            self.output.append(self.data)
        else:
            for i in range(self.data[2]):
                getattr(self.target, self.data[0])(self.data[1])
        self.state = [0, "", ""]
        self.data = ["", {}, 1]

    def format_to_line(self):
        with open(self.file_name, "r") as data_file:
                all_data = data_file.read()
        with open(self.file_name, "w") as write_file:
            for char in all_data:
                if char != " " and char != "\n":
                    write_file.write(char)

    def format_to_indent(self):
        self.format_to_line()
        with open(self.file_name, "r") as data_file:
                all_data = data_file.read()
        with open(self.file_name, "w") as write_file:
            current_level = 0
            for char in all_data:
                if char == "#":
                    current_level -= 1
                if char == ";":
                    write_file.write(char + "\n")
                    continue
                if char in self.commands[0]:
                    write_file.write("  "*current_level)
                write_file.write(char)
                if char in {"/", "?"}:
                    current_level += 1

class Compiler:
    def __init__(self, file_name):
        self.reader = Reader(file_name)

    def load(self, target, setup):
        data = self.reader.run_as_generator()
        target = target
        for packet in data:
            print(packet)
            for i in range(packet[2]):
                print(target)
                target = getattr(target, packet[0])(packet[1])

    def print_all_data(self):
        for i in self.reader.run_as_generator():
            print(i)