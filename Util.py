import glm


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

class RenderHelper(Geometry):
    @staticmethod
    def centrist_coords(coord_list):
        output = coord_list
        for i in range(len(output)):
            output[i] = (output[i]*2)-1
        return output

    @staticmethod
    def rotationCorrect(vertex_list, ref_vector):
        if ref_vector == glm.vec3(0):
            reversed_vertices = vertex_list[:]
            reversed_vertices.reverse()
            vertex_list.extend(reversed_vertices)
        else:
            for i in range(0, len(vertex_list), 3):
                a = glm.vec3(vertex_list[i]) - glm.vec3(vertex_list[i+1])
                b = glm.vec3(vertex_list[i+2]) - glm.vec3(vertex_list[i+1])
                n = glm.cross(a, b)
                t = n*ref_vector
                if sum((t > glm.vec3(0)).to_list()) >= 2:
                    vertex_list.insert(i+1, vertex_list.pop(i+2))
    
    @staticmethod
    def finalize(vertex_list, pos):
        vertices = []

        for vertex in vertex_list:
            vertices.extend(vertex)

        for i in range(len(vertices)):
            vertices[i] = float(vertices[i])

        return vertices

    @staticmethod
    def get_adjacents(pos, compare_to, output=list(), is_coords=False, compare_is_bool=True):
        if not is_coords:
            coords = Geometry.coords_from_index(pos)
        else:
            coords = pos
            
        count = 0
        if compare_is_bool:
            for i in range(3):
                test_coords = Geometry.invert_coords(coords, i)
                if compare_to[Geometry.index_from_coords(test_coords)]:
                    count+=1
        else:
            for i in range(3):
                test_coords = Geometry.invert_coords(coords, i)
                if compare_to.count(test_coords) == 1:
                    count+=1
                    output.extend(test_coords)
        return count

    @staticmethod
    def check_axials(pos1, pos2, compare_to, output=list(), is_coords=False):
        if not is_coords:
            coords1 = Geometry.coords_from_index(pos1)
            coords2 = Geometry.coords_from_index(pos2)
        else:
            coords1 = pos1
            coords2 = pos2

        count = 0

        test_coords1 = Geometry.invert_coords(coords1, [0, 1, 2])
        test_coords2 = Geometry.invert_coords(coords2, [0, 1, 2])

        if compare_to.count(test_coords1) > 0:
            output.extend(test_coords1)
            count+=1
        if compare_to.count(test_coords2) > 0:
            output.extend(test_coords2)
            count+=1

        return count

    @staticmethod
    def test_planar(points):
        x_unchanged = True
        y_unchanged = True
        z_unchanged = True
        for i in range(len(points)-1):
            if points[3][0] != points[i][0]:
                x_unchanged = False
            if points[3][1] != points[i][1]:
                y_unchanged = False
            if points[3][2] != points[i][2]:
                z_unchanged = False
            if not x_unchanged and not y_unchanged and not z_unchanged:
                return False
        return True