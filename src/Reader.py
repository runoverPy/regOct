from queue import Queue

class Reader:
    def __init__(self, target, file_name):
        self.target = target
        self.file_name = file_name
        self.commands = [
            {"!":"header", "?":"root", "/":"create_branch", "&":"fill_branch", "#":"close_branch"},     # Commands
            {'"':"set_value", "'":"set_value", "*":"set_iterations", "@":"set_vartag", ";":"finish"},   # Modifiers
            {'"':"load_char", "'":"load_int"}]                                                          # Parameters

        self.processes = ["assign_command", "assign_modifier", "run_modifier"]
        self.state = [0, "", ""]        # Active Process | Active Modifier | Active Parameter
        self.data = ["", {}, 1]         # Command | Parameters | Iterations 
        self.buffer = ["", "", 0]       # VarTag | DataString | Chars Remaining

    def run(self):
        with open(self.file_name, "r") as data_file:
                all_data = data_file.read()
                for b in all_data:
                    if b != " " and b != "\n":
                        getattr(self, self.processes[self.state[0]])(b)

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
        for i in range(self.data[2]):
            getattr(self.target, self.data[0])(self.data[1])
        self.state = [0, "", ""]
        self.data = ["", {}, 1]
