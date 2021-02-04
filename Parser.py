
class Parser():
    def __init__(self, main):
        self.main = main

def parseChunkData(target, chunkData):
    isReadingParameters = False
    isReadingIterations = False
    command = '' 
    params = ""
    iterations = 1
    for sym in chunkData:
        if sym != ' ':
            if sym == '(':
                isReadingParameters = True
                continue
            elif sym == ')':
                isReadingParameters = False
                continue
            elif isReadingParameters:
                params += sym
                continue
            if sym == '[':
                isReadingIterations = True
                continue
            elif sym == ']':
                isReadingIterations = False
                continue
            elif isReadingIterations:
                iterations = int(sym)
                continue
            if sym in validCommands:
                if command != "" and not isReadingParameters:
                    execute(target, command, params, iterations)
                    command = ""
                    iterations = 1
                    params = ""
                if sym not in expectsParams:
                    execute(target, sym, "", iterations)
                    iterations = 1
                else:
                    command = sym


def execute(target, command, params, iterations):
    for i in range(iterations):
        print(f'[{iterations}]{command}({params})')
        if command == "/":
            target.create_branch()
        elif command == "^":
            target.fill_branch(params)
        elif command == "#":
            target.close_branch()

expectsParams = {"^"}
validCommands = {"/", "^", "#"}

