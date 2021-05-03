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
        return sum(glm.i16vec3(coord_list) * glm.i16vec3(1,2,4) / 2**level)

    @staticmethod   
    def coord_gen(num):
        for i in range(8):
            yield glm.vec3(num) % glm.vec3(2, 4, 8) // glm.vec3(1, 2, 4)

    @staticmethod
    def coords_from_index(num, level=0):
        return (glm.vec3(num) % glm.vec3(2, 4, 8) // glm.vec3(1, 2, 4) * 2**level).to_list()
        
    @staticmethod
    def coord_addition(coord1, coord2):
        return (glm.vec3(coord1) + glm.vec3(coord2)).to_list()

    @staticmethod
    def coord_div(coord, denom):
        return (glm.vec3(coord) // denom).to_list()

    @staticmethod
    def coord_mod(coord, denom):
        return (glm.vec3(coord) % denom).to_list()

    @staticmethod
    def coord_compare_less(coord, value):
        if 1 in (glm.i16vec3(coord) < glm.i16vec3(value)):
            return False
        else:
            return True

class ToplessInt(int):
    """A virtual int that can only be used comparatively.
    It is always greater than the int it is compared to."""
    def __ge__(self, i:int) -> bool:
        return True

    def __gt__(self, i:int) -> bool:
        return True

    def __le__(self, i:int) -> bool:
        return False

    def __lt__(self, i:int) -> bool:
        return False

    def __eq__(self, i:int) -> bool:
        return False

    def __ne__(self, i:int) -> bool:
        return True

header_key = {"major":"0x0"}
root_key = {"level":"0x0", "pos":"0x4"}

if __name__ == "__main__":
    for i in range(8):
        print(Geometry.coords_from_index(i, 1), 1)