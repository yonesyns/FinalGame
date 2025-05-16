import pygame

class TileKind:
    def __init__(self, name, color, is_solid):
        self.name = name
        self.color = color
        self.is_solid = is_solid

class Map:
    def __init__(self, map_file, tile_kinds, tile_size):
        self.tile_kinds = tile_kinds
        self.tile_size = tile_size
        self.tiles = []
        self.start_pos = (1 * tile_size, 1 * tile_size)  # Default start
        self.end_pos = (18 * tile_size, 18 * tile_size)  # Default end
        
        with open(map_file, "r") as file:
            for y, line in enumerate(file):
                line = line.strip()
                if line:
                    row = [int(c) for c in line if c in '0123']  # Now includes 2 and 3
                    if row:
                        self.tiles.append(row)
        
        # Now find start and end positions
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if tile == 2:  # Start position
                    self.start_pos = (x * tile_size, y * tile_size)
                elif tile == 3:  # End position
                    self.end_pos = (x * tile_size, y * tile_size)
        
        print("Map loaded:")
        for row in self.tiles:
            print(row)
        print(f"Start position: {self.start_pos}")
        print(f"End position: {self.end_pos}")

    def draw(self, screen):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if tile < len(self.tile_kinds):  # Vérifie que l'index est valide
                    tile_kind = self.tile_kinds[tile]
                    rect = pygame.Rect(x * self.tile_size, y * self.tile_size, 
                                     self.tile_size, self.tile_size)
                    pygame.draw.rect(screen, tile_kind.color, rect)