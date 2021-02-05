import pygame


class World:
    def __init__(self, screen, scope):
        self.cubes = []
        self.scope = scope # scope corresponds to octree level, so a scope of 2 will show 16 leaves, min 2
        self.posn = [] # [x, y, z], [int, int, int], shows 

    def change_scope(self, change):
        pass

    def change_layer(self, change):
        pass

    def update(self):
        pass

class Main:
    def __init__(self, assembly):
        pygame.init()
        self.window = pygame.display.set_mode((600, 600))
        pygame.display.set_caption("super awesome octree viewer")
        self.screen = pygame.display.get_surface()
        self.assembly = assembly
