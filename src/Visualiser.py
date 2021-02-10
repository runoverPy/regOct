from .Structures import RegOct
from .Reader import Reader
from pygame.locals import *
from pygame.time import get_ticks
import pygame
import keyboard
import glm


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
        self.ticks = get_ticks()

    def change_posn(self):
        if get_ticks() - self.ticks >= 250: 
            if keyboard.is_pressed("up arrow"):
                self.posn[0] += 1
                self.ticks = get_ticks()
            if keyboard.is_pressed("down arrow"):
                self.posn[0] -= 1
                self.ticks = get_ticks()
            if keyboard.is_pressed("left arrow"):
                self.scope -= 1
                self.ticks = get_ticks()
            if keyboard.is_pressed("right arrow"):
                self.scope += 1
                self.ticks = get_ticks()
        if keyboard.is_pressed("W"):
            self.posn[2] -= 0.03 * 2**(self.scope - 3)
        if keyboard.is_pressed("A"):
            self.posn[1] -= 0.03 * 2**(self.scope - 3)
        if keyboard.is_pressed("S"):
            self.posn[2] += 0.03 * 2**(self.scope - 3)
        if keyboard.is_pressed("D"):
            self.posn[1] += 0.03 * 2**(self.scope - 3)

    def update_data(self):
        self.cubes = {}
        length = 2**self.scope + 1
        coords = glm.vec3([0, 0, 0])
        for i in range(length):
            coords[1] = i
            for j in range(length):
                coords[2] = j
                check_pos = (coords + self.posn).to_list()
                if glm.i16vec3(coords % 2**(leaf_data := self.octree.get(check_pos, "coords", "level", "default"))["level"]) == glm.i16vec3(0) and leaf_data["coords"] != None:
                    if (coord_str := ';'.join(str(d) for d in leaf_data["coords"])) not in self.cubes:
                        leaf_data["coords"] = (glm.vec3(leaf_data["coords"]) - self.posn).to_list()
                        self.cubes[coord_str] = leaf_data
   
    def edge_length(self, index):
        return 2**(index-self.scope)*(700)-25

    def edge_dist(self):
        return self.edge_length(0) + 25

    def update(self):
        for cube in self.cubes.items():
            cube_coords = cube[1]["coords"]
            cube_level = cube[1]["level"]
            block = pygame.Rect(cube_coords[1]*self.edge_dist(), cube_coords[2]*self.edge_dist(), self.edge_length(cube_level), self.edge_length(cube_level))
            pygame.draw.rect(self.screen, pygame.Color(255*cube[1]["default"], 255*cube[1]["default"], 255), block)

class Displayer:
    def __init__(self, assembly):
        pygame.init()
        self.window = pygame.display.set_mode((675, 675))
        pygame.display.set_caption("super awesome octree viewer")
        self.screen = pygame.display.get_surface()
        self.assembly = assembly

    @classmethod
    def load_file(cls, file_name):
        octree = RegOct
        return cls(octree)

    def has_ended(self):
        if keyboard.is_pressed("escape"):
            return True
        else:
            return False

    @staticmethod
    def display(octree):
        main = Displayer(octree)
        screen = main.screen
        world = World(screen, 2, octree)
        while not main.has_ended(): 
            pygame.event.get()
            screen.fill(pygame.Color(100,100,100))
            world.change_posn()   
            world.update_data()
            world.update()
            pygame.display.update()
