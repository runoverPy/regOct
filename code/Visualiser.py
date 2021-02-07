import pygame
from pygame.locals import *
import keyboard
import glm
from Structures import RegOct
assert pygame


"""
NOTICE
If you are using vs code, you might also see all the <sarcasm> magnificent {errors.count()} </sarcasm> errors.
"""

class World:
    def __init__(self, screen, scope, octree):
        self.screen = screen
        self.scope = scope # scope corresponds to max visible octree level, a scope of 0 will show 1 leaf, 1:4, 2:16 etc
        self.posn = glm.vec3(0, 0, 0) # [x, y, z], [int, int, int] bottom right corner of viewer
        self.heading = glm.vec3(1, 0, 0) # viewer faces positive x
        self.octree = octree

    def change_posn(self):
        if keyboard.is_pressed("W"):
            self.posn[2] += 0.005*2**self.scope
        if keyboard.is_pressed("A"):
            self.posn[1] += 0.005*2**self.scope
        if keyboard.is_pressed("S"):
            self.posn[2] -= 0.005*2**self.scope
        if keyboard.is_pressed("D"):
            self.posn[1] -= 0.005*2**self.scope

    def update_data(self):
        self.cubes = []
        length = 2**self.scope
        coords = glm.vec3([0, 0, 0])
        for i in range(length):
            coords[1] = i
            for j in range(length):
                coords[2] = j
                if glm.i16vec3(coords % 2**(leaf_level := self.octree.get(coords.to_list(), "level"))) == glm.i16vec3(0):
                    leaf_coords = coords + self.posn
                    print(coords)
                    self.cubes.append((leaf_coords.to_list(), leaf_level))



    def update(self):
        for cube in self.cubes:
            edge_length = 150*(2**cube[1]) + 25*(2**cube[1]-1)
            edge_dist = 175
            # print(cube[0][1]*edge_dist, cube[0][2]*edge_dist, edge_length, edge_length, cube[1])
            block = pygame.Rect(25 + cube[0][1]*edge_dist, 25 + cube[0][2]*edge_dist, edge_length, edge_length)
            pygame.draw.rect(self.screen, pygame.Color(100*cube[1], 255, 255), block)



class Main:
    def __init__(self, assembly):
        pygame.init() # @self: the error is only formal
        self.window = pygame.display.set_mode((725, 725))
        pygame.display.set_caption("super awesome octree viewer")
        self.screen = pygame.display.get_surface()
        self.assembly = assembly

    def has_ended(self):
        if keyboard.is_pressed("escape"):
            return True
        else:
            return False


if __name__ == "__main__":
    octree = RegOct.direct(2, "tests/test.onc")
    main = Main(octree)
    screen = main.screen
    world = World(screen, 2, octree)
    while not main.has_ended(): 
        screen.fill(pygame.Color(100,100,100))
        world.change_posn()   
        world.update_data()
        world.update()
        pygame.display.update()