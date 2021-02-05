from enum import Enum

class RegOctLoader:
    def __init__(self, target, file_name):
        self.target = target
        self.commands = [
            {"/":"create_branch", "@":"fill_branch", "#":"close_branch"},
            {';'},
            {'"':"load_str", "'":"load_int", "*":"set_iterations", ";":"push_command"}]

        self.processes = ["assign_command", "assign_modifier", "assign_parameter"]
        self.state = [0, "", "", [], 0, 1]          # process, current_command, current_mod, out_list, out_list_index, iterations

        with open(file_name, "r") as data_file:
            all_data = data_file.read()
            for b in all_data:
                if b != " " and b != "\n":
                    getattr(self, self.processes[self.state[0]])(b)

    def assign_command(self, args):
        self.state[0] = 1
        self.state[1] = self.commands[0][args]

    def assign_modifier(self, args):
        self.state[2] = ""
        if args not in self.commands[1]:
            self.state[0] = 2
            self.state[2] = self.commands[2][args]
        else:
            getattr(self, self.commands[2][args])(args)

    def assign_parameter(self, args):
        getattr(self, self.state[2])(args)

    def load_str(self, args):
        self.state[0] = 1
        self.state[3].append(str(args))

    def load_int(self, args):
        self.state[0] = 1
        self.state[3].append(int(args))

    def set_iterations(self, args):
        self.state[0] = 1
        self.state[5] = int(args)

    def push_command(self, args):
        for i in range(self.state[5]):
            getattr(self.target, self.state[1])(self.state[3])
        self.state = [0, "", "", [], 0, 1] 

if __name__ == "__main__":
    RegOctLoader(None, "test.onc")