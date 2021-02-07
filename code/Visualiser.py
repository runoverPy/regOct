import pygame
from pygame.locals import *
import glm
from Structures import RegOct

class World:
    def __init__(self, screen, scope, octree):
        self.cubes = []
        self.screen = screen
        self.scope = scope # scope corresponds to max visible octree level, a scope of 0 will show 1 leaf, 1:4, 2:16 etc
        self.posn = glm.vec3(0, 0, 0) # [x, y, z], [int, int, int] bottom right corner of viewer
        self.heading = glm.vec3(1, 0, 0) # viewer faces positive x
        self.octree = octree

    def change_scope(self, change):
        pass

    def change_layer(self, change):
        pass

    def change_posn(self):
        key_state = pygame.key.get_pressed()
        if key_state[K_w]:
            self.posn[1] += 0.1*2**self.scope
        elif key_state[K_s]:
            self.posn[1] -= 0.1*2**self.scope
        elif key_state[K_a]:
            self.posn[2] += 0.1*2**self.scope
        elif key_state[K_d]:
            self.posn[2] -= 0.1*2**self.scope

    def update_data(self):
        length = 2**self.scope
        coords = glm.vec3([0, 0, 0])
        for i in range(length):
            coords[1] = i + self.posn[1]
            for j in range(length):
                coords[2] = j + self.posn[2]
                leaf_coords = coords
                if glm.i16vec3(leaf_coords % 2**(leaf_level := self.octree.get(coords, "level"))) == glm.i16vec3(0):
                    self.cubes.append((coords.to_list(), leaf_level))

    def update(self):
        for cube in self.cubes:
            edge_length = 150*(2**cube[1]) + 25*(2**cube[1]-1)
            edge_dist = 175*(2**cube[1])
            # print(cube[0][1]*edge_dist, cube[0][2]*edge_dist, edge_length, edge_length)
            block = pygame.Rect(25 + cube[0][1]*edge_dist, 25 + cube[0][2]*edge_dist, edge_length, edge_length)
            pygame.draw.rect(self.screen, pygame.Color(255, 255, 255), block)



class Main:
    def __init__(self, assembly):
        pygame.init() # @self: the error is only formal
        self.window = pygame.display.set_mode((725, 725))
        pygame.display.set_caption("super awesome octree viewer")
        self.screen = pygame.display.get_surface()
        self.assembly = assembly

    def has_ended(self):
        key_state = pygame.key.get_pressed()
        if key_state[K_ESCAPE]:
            return True
        else:
            return False


if __name__ == "__main__":
    octree = RegOct.direct(2, "tests/test.onc")
    main = Main(octree)
    screen = main.screen
    world = World(screen, 2, octree)
    while not main.has_ended(): 
        screen.fill(pygame.Color(55,55,55))
        world.change_posn()   
        world.update_data()
        world.update()
        pygame.display.update()