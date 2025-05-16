import pygame
import random

class Diamond:
    def __init__(self, grid_x, grid_y, tile_size):
        self.collected = False
        self.size = tile_size // 4
        
        # Positionnement au centre de la tuile
        self.rect = pygame.Rect(
            grid_x * tile_size + (tile_size - self.size) // 2,  # Centre X
            grid_y * tile_size + (tile_size - self.size) // 2,  # Centre Y
            self.size,
            self.size
        )
        self.color = (0, 255, 255)  # Cyan vif
        self.collected = False

    def draw(self, screen):
        if not self.collected:
            pygame.draw.rect(screen, self.color, self.rect)

def generate_diamonds(game_map, tile_size, density=0.3):
    """Génère des diamants sur les cases non-solides"""
    diamonds = []
    for y, row in enumerate(game_map.tiles):
        for x, tile_index in enumerate(row):
            # Vérifie si la case est un sol (non mur)
            if not game_map.tile_kinds[tile_index].is_solid:
                if random.random() < density:
                    diamonds.append(Diamond(x, y, tile_size))
    return diamonds