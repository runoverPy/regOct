import glm

class ToasterBathError(Exception):
    def __init__(self):
        self.message = "\nA terminally fatal error has ocurred during execution. \nPlease start an issue on github and submit the entire traceback.\n(paths containing compromising information should be removed)"
        super().__init__(self.message)

class SubdivisionIndexError(Exception):
    def __init__(self, value):
        self.value = value
        self.message = "Subdivision index below zero"
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}: {self.value}'

class InvalidRequestCallError(Exception):
    def __init__(self, called_by, request):
        self.request = request
        self.called_by = called_by
        self.message = "Has no Attribute"
        super().__init__(self.message)

    def __str__(self):
        return f'{self.called_by} {self.message}: {self.request}'

class AttributeDesynchronisationError(Exception):
    def __init__(self):
        self.message = "File data incompatible with given attribute layout"
        super().__init__(self.message)

class UnboundVartagError(Exception):
    def __init__(self, vartag, data):
        self.message = f"Vartag {vartag} not found in data {data.keys()}"
        super().__init__(self.message)

class Geometry():
    @staticmethod
    def index_from_coords(coord_list, level=0):
        output = 0
        output += int(1*coord_list[0]/2**level)
        output += int(2*coord_list[1]/2**level)
        output += int(4*coord_list[2]/2**level)
        return output

    @staticmethod
    def coords_from_index(num, level=0):
        output = [0, 0, 0]
        output[0] = int(int(num%2)*(2**level))
        output[1] = int(int((num%4)/2)*(2**level))
        output[2] = int(int(num/4)*(2**level))
        return output

    @staticmethod
    def coord_addition(coord1, coord2):
        output = coord1[:]
        for i in range(len(output)):
            output[i] += coord2[i]
        return output

    @staticmethod
    def coord_div(coord, denom):
        output = []
        for i in range(len(coord)):
            output.append(int(coord[i] / denom))
        return output

    @staticmethod
    def coord_mod(coord, denom):
        output = []
        for i in range(len(coord)):
            output.append(int(coord[i] % denom))
        return output

    @staticmethod
    def coord_compare_less(coord, value):
        for num in coord:
            if num < value:
                break
        else:
            return True
        return False

    @staticmethod
    def invert_coords(coord_list, pos):
        output = list(coord_list)
        if type(pos) == list:
            for i in pos:
                output[i] = abs(coord_list[i] - 1)
        else:
            output[pos] = abs(coord_list[pos] - 1)
        return output

if __name__ == "__main__":
    raise ToasterBathError