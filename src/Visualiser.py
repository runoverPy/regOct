import sys
from .Structures import Octree
from .Reader import Reader
import pygame
from pygame.locals import *
from pygame.time import get_ticks
import glm
import keyboard

class World:
    """The rendering protocol is out of date and must be updated, this class is currently inoperable."""
    def __init__(self, screen, scope, octree):
        self.screen = screen
        self.scope = scope # scope corresponds to max visible octree level, a scope of 0 will show 1 leaf, 1:4, 2:16 etc
        self.posn = glm.vec3(1, 0, 0) # [x, y, z], [int, int, int] bottom right corner of viewer
        self.heading = glm.vec3(1, 0, 0) # viewer faces positive x
        self.octree = octree
        self.ticks = get_ticks()
        self.last_ticks = get_ticks()

    def change_posn(self):
        if get_ticks() - self.ticks >= 250: 
            if keyboard.is_pressed("up arrow"):
                self.posn[0] += 1
                self.ticks = get_ticks()
            if keyboard.is_pressed("down arrow"):
                self.posn[0] -= 1
                self.ticks = get_ticks()
            if keyboard.is_pressed("left arrow") and self.scope > 0:
                self.scope -= 1
                self.ticks = get_ticks()
            if keyboard.is_pressed("right arrow"):
                self.scope += 1
                self.ticks = get_ticks()
        delta_time = get_ticks() - self.last_ticks
        self.last_ticks = get_ticks()
        if keyboard.is_pressed("W"):
            self.posn[2] -= 0.03 * delta_time * 2**(self.scope - 3)
        if keyboard.is_pressed("A"):
            self.posn[1] -= 0.03 * delta_time * 2**(self.scope - 3)
        if keyboard.is_pressed("S"):
            self.posn[2] += 0.03 * delta_time * 2**(self.scope - 3)
        if keyboard.is_pressed("D"):
            self.posn[1] += 0.03 * delta_time * 2**(self.scope - 3)

    def update_data(self):
        self.cubes = []
        length = 2**self.scope
        bottom_limit = glm.vec3(0) - self.posn
        top_limit = glm.vec3(length) - self.posn
        for item in self.octree.map():            
            if item["coords"][0]//2**item["level"] == self.posn[0]//2**item["level"]:
                self.cubes.append(item)

   
    def edge_length(self, index):
        return 2**(index-self.scope)*(700)-25

    def edge_dist(self):
        return self.edge_length(0) + 25

    def draw(self):
        for cube in self.cubes:
            cube_coords = glm.vec3(cube["coords"]) - self.posn
            cube_level = cube["level"]
            block = pygame.Rect(cube_coords[1]*self.edge_dist(), cube_coords[2]*self.edge_dist(), self.edge_length(cube_level), self.edge_length(cube_level))
            color = glm.vec3(int(cube["void"])*255).to_list()
            pygame.draw.rect(self.screen, pygame.Color(color), block)

    def print_mouse_pos(self):
        sys.stdout.write(f'\r{pygame.mouse.get_pos()}        ')

class Displayer:
    def __init__(self, octree):
        pygame.init()
        self.window = pygame.display.set_mode((675, 675))
        pygame.display.set_caption("super awesome octree viewer")
        self.screen = pygame.display.get_surface()
        screen = self.screen
        world = World(screen, 3, octree)
        while not keyboard.is_pressed("escape"):    
            pygame.event.get()
            screen.fill(pygame.Color(100,100,100))
            world.change_posn()   
            world.update_data()
            world.draw()
            world.print_mouse_pos()
            pygame.display.update()