import glm


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